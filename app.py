import streamlit as st
import requests
import statistics
import datetime

API_KEY = "AIzaSyDu-I4a5yIUi6AdGwiGT5oCvMkQxtDPvXc"

st.title("YouTube KOL 分析工具")

channel_url = st.text_input("请输入YouTube频道链接")
price = st.number_input("请输入合作费用 (USD)", min_value=0.0)

if st.button("开始分析"):

    try:
        # 提取频道名
        if "@" in channel_url:
            channel_name = channel_url.split("@")[-1]
        else:
            st.error("请输入 @username 类型频道链接")
            st.stop()

        # 搜索频道ID
        search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={channel_name}&key={API_KEY}"
        res = requests.get(search_url).json()

        if not res.get("items"):
            st.error("未找到频道")
            st.stop()

        channel_id = res["items"][0]["snippet"]["channelId"]

        # 获取上传列表
        channel_info = requests.get(
            f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={API_KEY}"
        ).json()

        uploads = channel_info["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # 最近50个视频
        playlist = requests.get(
            f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&playlistId={uploads}&key={API_KEY}"
        ).json()

        video_ids = []
        publish_dates = []

        for v in playlist["items"]:
            video_ids.append(v["contentDetails"]["videoId"])
            publish_dates.append(v["contentDetails"]["videoPublishedAt"])

        # 获取统计
        stats = requests.get(
            f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={','.join(video_ids)}&key={API_KEY}"
        ).json()

        views_all = []
        views30 = []
        views90 = []

        now = datetime.datetime.utcnow()

        for i, v in enumerate(stats["items"]):
            view = int(v["statistics"]["viewCount"])
            publish_time = datetime.datetime.strptime(
                publish_dates[i], "%Y-%m-%dT%H:%M:%SZ"
            )
            age_days = (now - publish_time).days

            views_all.append(view)
            if age_days <= 30:
                views30.append(view)
            if age_days <= 90:
                views90.append(view)

        if not views_all:
            st.error("无法获取频道数据")
            st.stop()

        # 计算指标
        avg30 = sum(views30) / len(views30) if views30 else 0
        avg90 = sum(views90) / len(views90) if views90 else 0
        median_views = statistics.median(views_all)

        # CPM
        cpm30 = price / (avg30 / 1000) if avg30 else 0
        cpm90 = price / (avg90 / 1000) if avg90 else 0
        cpm_median = price / (median_views / 1000) if median_views else 0

        # 建议报价（CPM 30-50）
        suggest_low = (median_views / 1000) * 30
        suggest_high = (median_views / 1000) * 50

        # 显示结果
        st.subheader("KOL数据分析")
        st.write("近30天发布视频数量:", len(views30))
        st.write("近30天平均播放量:", int(avg30))
        st.write("近90天平均播放量:", int(avg90))
        st.write("中位数播放量:", int(median_views))

        st.subheader("CPM分析")
        st.write("近30天平均播放CPM:", round(cpm30, 2))
        st.write("近90天平均播放CPM:", round(cpm90, 2))
        st.write("中位数播放CPM:", round(cpm_median, 2))

        st.subheader("建议报价")
        st.write(
            "建议合作价格区间:",
            int(suggest_low),
            "~",
            int(suggest_high),
            "USD"
        )

        st.subheader("合作判断")
        if avg90 < 5000:
            st.error("❌ 播放量低于5000")
        elif price > 2000:
            st.error("❌ 报价超过2000")
        elif cpm30 > 30:
            st.error("❌ CPM过高")
        else:
            st.success("✅ 可以合作")

    except Exception as e:
        st.error(f"分析失败: {e}")
