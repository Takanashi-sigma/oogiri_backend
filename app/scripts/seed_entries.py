import asyncio
from sqlalchemy import select

from app.core.database import AsyncSessionLocal  # ← 君の database.py に合わせて変える
from app.model.user_model import User
from app.model.entry_model import Entry
from app.model.contest_participation_model import ContestParticipation


ANSWERS = [
    "レジ袋を断るために最初から商品をポケットに入れる",
    "水道代節約のために涙で顔を洗う",
    "シャワーは雨の日限定",
    "電気代節約のために雷待ち生活",
    "冷蔵庫を使わず冬にベランダを冷蔵庫扱いする",
    "スーパーの試食でフルコースを組む",
    "Wi-Fi代節約のためにカフェの外で粘る",
    "節約のため友達の家を第二の実家にする",
    "ティッシュは乾かして再利用",
    "歯磨き粉を最後まで使うためハサミではなく解体する",
    "暖房代節約で家族全員こたつの一点集中",
    "電車賃節約のため目的地まで気持ちで移動する",
    "カップ麺のスープを翌日の鍋にする",
    "洗濯は風の強い日に服ごと外に立つ",
    "節約しすぎてついに呼吸を浅くした",
    "エアコンの代わりに気合いで南国だと思い込む",
    "外食は全部『人の一口』で済ませる",
    "スマホ代節約のため機内モードで生きる",
    "家賃節約のため押し入れを本宅にする",
    "水を減らしたいのでなるべく感動しない",
    "節約本を買う金がもったいないから図書館で立ち読み",
    "電気代が高いので日没と同時に寝る",
    "節約のため美容院ではなく扇風機の風で整える",
    "おにぎりを買わずに米を見ることで空腹をごまかす",
    "節約のため出かけない、というより外界を断つ",
    "冷房代節約でコンビニのドア前に住む",
    "節約のため欲望をサブスク解除した",
    "風呂は家族の思い出が濃くなるまでお湯を替えない",
    "節約のため祝日だけ人間らしい生活をする",
    "電球が切れたので暗闇に目を慣らした",
    "節約しすぎて最終的に通貨を信用しなくなった",
    "節約のため傘を買わず全部『小雨判定』にする",
    "コンセントを抜きすぎて家電に信用されていない",
    "冷蔵庫を開ける回数を減らすため中身を全部暗記した",
    "節約で外出を減らした結果、季節をニュースで知る",
    "服を買わないため去年の自分に合わせて痩せる",
    "節約のため誕生日プレゼントは去年もらった物を回す",
    "電気代節約で夜は家族全員しりとりだけで過ごす",
    "水道代節約のため食器は次の料理で洗う",
    "節約しすぎてレシートを家計簿兼メモ帳兼しおりにする",
    "節約のためATMに行かず残高を見ない",
    "暖房代節約で『寒い』と言った人から罰金を取る",
    "節約のため旅行は地図を見て行った気になる",
    "お茶代節約で2リットルの水に気持ちだけ麦茶を入れる",
    "節約しすぎてついに『無料』に課金し始めた",
    "ガス代節約のため料理を全部『余熱でいける』と言い張る",
    "節約のためネトフリは友達の感想だけで観たことにする",
    "節約でペットボトルを使い回しすぎて家族より長生き",
    "節約のため朝食を『昨日の余韻』で済ませる",
    "最終的に財布を持たないことで出費の原因を根絶した",
]


async def seed_entries() -> None:
    contest_id = 1

    async with AsyncSessionLocal() as db:
        # 50ユーザー取得
        result = await db.execute(
            select(User).order_by(User.id).limit(50)
        )
        users = result.scalars().all()

        if len(users) < 50:
            print(f"ユーザー数が足りません。必要: 50, 現在: {len(users)}")
            return

        created_count = 0

        for user, answer in zip(users, ANSWERS):
            # participation が無ければ作る
            result = await db.execute(
                select(ContestParticipation).where(
                    ContestParticipation.contest_id == contest_id,
                    ContestParticipation.user_id == user.id,
                )
            )
            participation = result.scalar_one_or_none()

            if participation is None:
                participation = ContestParticipation(
                    contest_id=contest_id,
                    user_id=user.id,
                    has_submitted_entry=True,
                    evaluation_count=0,
                )
                db.add(participation)
            else:
                participation.has_submitted_entry = True

            # entry が既にあるならスキップ
            result = await db.execute(
                select(Entry).where(
                    Entry.contest_id == contest_id,
                    Entry.user_id == user.id,
                )
            )
            existing_entry = result.scalar_one_or_none()

            if existing_entry is not None:
                continue

            entry = Entry(
                contest_id=contest_id,
                user_id=user.id,
                content=answer,
                rating=1500,
                rd=350,
                volatility=0.06,
                comparisons_count=0,
                wins=0,
                losses=0,
            )
            db.add(entry)
            created_count += 1

        await db.commit()
        print(f"{created_count}件の回答を contest_id={contest_id} に追加しました。")


if __name__ == "__main__":
    asyncio.run(seed_entries())