"""
将 6551 API 爬取的 @FabricFND 推文存入 Chroma Cloud
用法: python scripts/sync_tweets_to_chroma.py FabricFND
"""
import os, httpx, json, asyncio, hashlib
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# 6551 API config
TWITTER_TOKEN = os.getenv("TWITTER_TOKEN")
TWITTER_API_BASE = "https://ai.6551.io"

# Chroma Cloud config
CHROMA_API_KEY = os.getenv("CHROMA_CLOUD_API_KEY")
CHROMA_TENANT = os.getenv("CHROMA_CLOUD_TENANT")
CHROMA_DB = os.getenv("CHROMA_CLOUD_DATABASE")


def get_chroma_client():
    """获取 Chroma Cloud 客户端"""
    import chromadb
    return chromadb.CloudClient(
        tenant=CHROMA_TENANT,
        database=CHROMA_DB,
        api_key=CHROMA_API_KEY,
    )


async def fetch_tweets(username: str, max_results: int = 100) -> list[dict]:
    """从 6551 API 拉取用户推文"""
    headers = {"Authorization": f"Bearer {TWITTER_TOKEN}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=30, headers=headers) as client:
        # 获取用户信息
        r1 = await client.post(f"{TWITTER_API_BASE}/open/twitter_user_info", json={"username": username})
        user_info = r1.json().get("data", {}) if r1.status_code == 200 else {}
        
        # 获取推文
        r2 = await client.post(
            f"{TWITTER_API_BASE}/open/twitter_user_tweets",
            json={"username": username, "maxResults": max_results, "product": "Latest", "includeReplies": True, "includeRetweets": True}
        )
        tweets = r2.json().get("data", []) if r2.status_code == 200 else []
        
        return user_info, tweets


def sync_to_chroma(username: str, user_info: dict, tweets: list[dict]):
    """将推文存入 Chroma Cloud"""
    client = get_chroma_client()
    
    # 创建或获取项目推文 collection
    collection_name = f"{username.lower()}_tweets"
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine", "project": username}
    )
    
    existing_count = collection.count()
    print(f"Collection '{collection_name}': 已有 {existing_count} 条记录")
    
    # 准备数据
    ids = []
    documents = []
    metadatas = []
    
    for tweet in tweets:
        tweet_id = tweet.get("id", hashlib.md5(tweet.get("text", "").encode()).hexdigest())
        text = tweet.get("text", "").strip()
        if not text:
            continue
        
        ids.append(str(tweet_id))
        documents.append(text)
        metadatas.append({
            "username": username,
            "created_at": tweet.get("createdAt", ""),
            "likes": tweet.get("favoriteCount", 0),
            "retweets": tweet.get("retweetCount", 0),
            "replies": tweet.get("replyCount", 0),
            "source": "6551_api",
            "synced_at": datetime.now().isoformat(),
        })
    
    if ids:
        # upsert: 已存在的更新，不存在的新增
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        print(f"✅ 同步完成: {len(ids)} 条推文 → Chroma Cloud '{collection_name}'")
        print(f"   Collection 现有: {collection.count()} 条记录")
    else:
        print("⚠️ 没有推文可同步")
    
    # 也存用户基本信息到单独的 collection
    if user_info and user_info.get("success"):
        project_col = client.get_or_create_collection(
            name="project_profiles",
            metadata={"hnsw:space": "cosine"}
        )
        bio = user_info.get("description", "")
        if bio:
            project_col.upsert(
                ids=[f"profile_{username}"],
                documents=[f"{user_info.get('name', username)}: {bio}"],
                metadatas=[{
                    "username": username,
                    "name": user_info.get("name", ""),
                    "followers": user_info.get("followersCount", 0),
                    "following": user_info.get("friendsCount", 0),
                    "tweet_count": user_info.get("statusesCount", 0),
                    "source": "6551_api",
                    "synced_at": datetime.now().isoformat(),
                }]
            )
            print(f"✅ 用户信息已存入 'project_profiles'")


async def main():
    import sys
    username = sys.argv[1] if len(sys.argv) > 1 else "FabricFND"
    
    print(f"=== 同步 @{username} 推文到 Chroma Cloud ===")
    print(f"6551 API → Chroma Cloud ({CHROMA_DB})")
    print()
    
    # Step 1: 拉取
    print("Step 1: 从 6551 API 拉取推文...")
    user_info, tweets = await fetch_tweets(username)
    print(f"   拉取到 {len(tweets)} 条推文")
    if user_info.get("success"):
        print(f"   用户: {user_info.get('name')} (@{user_info.get('screenName')}), {user_info.get('followersCount')} followers")
    print()
    
    # Step 2: 存入 Chroma
    print("Step 2: 存入 Chroma Cloud...")
    sync_to_chroma(username, user_info, tweets)
    print()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
