import math
from dataclasses import dataclass

GLICKO2_SCALE: float = 173.7178
DEFAULT_RATING: float = 1500.0
DEFAULT_RD: float = 350.0
DEFAULT_VOLATILITY: float = 0.06

MIN_RD: float = 30.0
MAX_RD: float = 350.0


@dataclass
class GlickoPlayer:
    rating: float
    rd: float
    volatility: float


@dataclass
class GlickoMatch:
    opponent_rating: float
    opponent_rd: float
    score: float


def to_mu(rating: float) -> float:
    return (rating - DEFAULT_RATING) / GLICKO2_SCALE


def to_phi(rd: float) -> float:
    return rd / GLICKO2_SCALE


def to_rating(mu: float) -> float:
    return mu * GLICKO2_SCALE + DEFAULT_RATING


def to_rd(phi: float) -> float:
    return phi * GLICKO2_SCALE


def clamp_rd(rd: float) -> float:
    return max(MIN_RD, min(rd, MAX_RD))


def g(phi: float) -> float:
    return 1.0 / math.sqrt(1.0 + 3.0 * (phi ** 2) / (math.pi ** 2))


def expected_score(mu: float, mu_j: float, phi_j: float) -> float:
    x = -g(phi_j) * (mu - mu_j)

    if x > 700:
        return 0.0
    if x < -700:
        return 1.0

    return 1.0 / (1.0 + math.exp(x))


def calculate_v(mu: float, matches: list[GlickoMatch]) -> float:
    inverse_v = 0.0

    for match in matches:
        mu_j = to_mu(match.opponent_rating)
        phi_j = to_phi(clamp_rd(match.opponent_rd))
        e_val = expected_score(mu, mu_j, phi_j)
        g_val = g(phi_j)
        inverse_v += (g_val ** 2) * e_val * (1.0 - e_val)

    if inverse_v <= 0.0:
        raise ValueError("calculate_v failed: inverse_v is zero or negative")

    return 1.0 / inverse_v


def rate_player(
    player: GlickoPlayer,
    matches: list[GlickoMatch],
) -> GlickoPlayer:
    mu = to_mu(player.rating)
    safe_rd = clamp_rd(player.rd)
    phi = to_phi(safe_rd)

    # 壊れたDB値を使わず、常に固定値を使う
    sigma = DEFAULT_VOLATILITY

    if not matches:
        phi_star = math.sqrt(phi**2 + sigma**2)
        return GlickoPlayer(
            rating=player.rating,
            rd=clamp_rd(to_rd(phi_star)),
            volatility=DEFAULT_VOLATILITY,
        )

    v = calculate_v(mu, matches)

    total = 0.0
    for match in matches:
        mu_j = to_mu(match.opponent_rating)
        phi_j = to_phi(clamp_rd(match.opponent_rd))
        e_val = expected_score(mu, mu_j, phi_j)
        g_val = g(phi_j)
        total += g_val * (match.score - e_val)

    phi_star = math.sqrt(phi**2 + sigma**2)
    phi_prime = 1.0 / math.sqrt((1.0 / (phi_star**2)) + (1.0 / v))
    mu_prime = mu + (phi_prime**2) * total

    return GlickoPlayer(
        rating=to_rating(mu_prime),
        rd=clamp_rd(to_rd(phi_prime)),
        volatility=DEFAULT_VOLATILITY,
    )


def rate_1vs1(
    a_rating: float,
    a_rd: float,
    a_volatility: float,
    b_rating: float,
    b_rd: float,
    b_volatility: float,
    a_score: float,
) -> dict:
    b_score = 1.0 - a_score

    a_player = GlickoPlayer(
        rating=a_rating,
        rd=a_rd,
        volatility=DEFAULT_VOLATILITY,
    )
    b_player = GlickoPlayer(
        rating=b_rating,
        rd=b_rd,
        volatility=DEFAULT_VOLATILITY,
    )

    a_update = rate_player(
        player=a_player,
        matches=[
            GlickoMatch(
                opponent_rating=b_rating,
                opponent_rd=b_rd,
                score=a_score,
            )
        ],
    )

    b_update = rate_player(
        player=b_player,
        matches=[
            GlickoMatch(
                opponent_rating=a_rating,
                opponent_rd=a_rd,
                score=b_score,
            )
        ],
    )

    return {
        "a_rating": a_update.rating,
        "a_rd": a_update.rd,
        "a_volatility": a_update.volatility,
        "b_rating": b_update.rating,
        "b_rd": b_update.rd,
        "b_volatility": b_update.volatility,
    }