
import asyncio
import json
import requests
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import itertools
from flask import Flask, jsonify, send_file, render_template
import polars as pl

app = Flask(__name__)

# Hàm cập nhật dữ liệu


async def update_data():
    global result_df
    async def main():
        global hotel_responses, result_df
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()


        try:
            # Mở trang web đăng nhập
            page.goto("https://id.bluejaypms.com/login")

            # Chờ cho ngôn ngữ load xong và chọn ngôn ngữ
            page.wait_for_selector("select[name='ddlLangCode']", timeout=30000)
            page.select_option("select[name='ddlLangCode']", "vi-VN")

            # Điền thông tin đăng nhập
            page.fill("input[name='txtEmail']", "ngan.lalahouse@gmail.com")
            page.fill("input[name='txtPassword']", "Hotelhelper@2024")

            # Nhấn nút đăng nhập
            page.click("button#lkLogin")

            # Chờ tải trang sau khi đăng nhập
            page.wait_for_selector("a#lvHotels_lbtNameHotel_0", timeout=30000)

            # Nhấn vào khách sạn đầu tiên
            page.click("a#lvHotels_lbtNameHotel_0")

            # Chờ tải trang khách sạn
            page.wait_for_selector("div#hotel-detail", timeout=30000)

            # Lấy cookies từ trang
            cookies = page.context.cookies()
            keys_to_keep = [
                "ASP.NET_SessionId", "HtLanguage", "HtToken", "HtHotelId", "HtBaseDir"
            ]
            filtered_cookies = [cookie for cookie in cookies if cookie['name'] in keys_to_keep]

            # Danh sách khách sạn mới
            new_ht_hotel_id_list = ["5998", "6001", "6062"]
            hotel_responses = []
            today = datetime.today()

            # Định dạng ngày theo kiểu YYYY-MM-DD
            from_date = today.strftime('%Y-%m-%d')
            t = 30
            # Tính ngày 10 ngày sau
            to_date = today + timedelta(days=t)
            to_date = to_date.strftime('%Y-%m-%d')

            # Gửi yêu cầu với từng HtHotelId
            for new_ht_hotel_id in new_ht_hotel_id_list:
                for cookie in filtered_cookies:
                    if cookie['name'] == 'HtHotelId':
                        cookie['value'] = new_ht_hotel_id

                cookie_header = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in filtered_cookies])

                url = "https://id.bluejaypms.com/app/Room/GetRoomAvails"
                headers = {
                    "Accept": "*/*", "Accept-Encoding": "gzip, deflate, br, zstd", "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
                    "Content-Type": "application/json; charset=UTF-8", "Referer": "https://id.bluejaypms.com/app/calendar",
                    "Origin": "https://id.bluejaypms.com", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                    "Cookie": cookie_header
                }

                data = [
                    {"Action": "UpdateAvail", "RoomTypeId": "9197", "FromDate": from_date, "ToDate": to_date},
                    {"Action": "UpdateAvail", "RoomTypeId": "9198", "FromDate": from_date, "ToDate": to_date},
                    {"Action": "UpdateAvail", "RoomTypeId": "9199", "FromDate": from_date, "ToDate": to_date},
                    {"Action": "UpdateAvail", "RoomTypeId": "9207", "FromDate": from_date, "ToDate": to_date},
                    {"Action": "UpdateAvail", "RoomTypeId": "9208", "FromDate": from_date, "ToDate": to_date},
                    {"Action": "UpdateAvail", "RoomTypeId": "9206", "FromDate": from_date, "ToDate": to_date},
                    {"Action": "UpdateAvail", "RoomTypeId": "9555", "FromDate": from_date, "ToDate": to_date},
                    {"Action": "UpdateAvail", "RoomTypeId": "9556", "FromDate": from_date, "ToDate": to_date},
                    {"Action": "UpdateAvail", "RoomTypeId": "9557", "FromDate": from_date, "ToDate": to_date},
                    {"Action": "UpdateAvail", "RoomTypeId": "9558", "FromDate": from_date, "ToDate": to_date},
                    {"Action": "UpdateAvail", "RoomTypeId": "9559", "FromDate": from_date, "ToDate": to_date},
                ]

                json_data = json.dumps(data)
                response = requests.post(url, headers=headers, data=json_data)
                if response.status_code == 200:
                    hotel_responses.append(response.json())

        finally:
            browser.close()


        bt = list(itertools.chain.from_iterable(hotel_responses))


        # Dữ liệu phòng và khách sạn


        rooms_data = [
            {"RoomType_Id": "9206", "room_name": "Deluxe Double Room"},
            {"RoomType_Id": "9207", "room_name": "King room with garden view"},
            {"RoomType_Id": "9208", "room_name": "King room with Balcony"},
            {"RoomType_Id": "9197", "room_name": "Deluxe Double Room"},
            {"RoomType_Id": "9198", "room_name": "King room with garden view"},
            {"RoomType_Id": "9199", "room_name": "King room with Balcony"},
            {"RoomType_Id": "9555", "room_name": "Superior"},
            {"RoomType_Id": "9556", "room_name": "Deluxe"},
            {"RoomType_Id": "9557", "room_name": "Luxury"},
            {"RoomType_Id": "9558", "room_name": "Queen"},
            {"RoomType_Id": "9559", "room_name": "Standard"},
        ]
        rooms_df = pl.DataFrame(rooms_data)


        hotels_data = [
            {"HotelId": "6001", "hotel_name": "Ben Thanh Inn"},
            {"HotelId": "5998", "hotel_name": "Elegant Feel Inn"},
            {"HotelId": "6062", "hotel_name": "MG Daisy"},
        ]
        hotels_df = pl.DataFrame(hotels_data)


        df = pl.DataFrame(bt)




        start_date = datetime.today()
        end_date = start_date + timedelta(days=30)


        # Generate date range and collect it to list
        date_range_expr = pl.date_range(start=start_date, end=end_date, eager=True)
        date_range = date_range_expr.to_list()
        # Xử lý các cột thời gian và giá trị
        df = df.with_columns([
            pl.col("SellFrom").str.to_datetime().cast(pl.Date).alias("SellFrom"),  # Cập nhật cột SellFrom
            pl.col("SellTo").str.to_datetime().cast(pl.Date).alias("SellTo"),
            pl.col("RoomType_Id").cast(pl.Utf8),
            pl.col("HotelId").cast(pl.Utf8)  # Chuyển RoomType_Id sang kiểu str
  # Chuyển RoomType_Id sang kiểu str
       # Cập nhật cột SellTo
        ])


        # Ensure the dates are defined before they are used
        start_date = datetime.today().date()  # Use only the date part (no time)
        end_date = start_date + timedelta(days=30)


        # Generate date range and collect it to list
        date_range_expr = pl.date_range(start=start_date, end=end_date, eager=True)
        date_range = date_range_expr.to_list()
        date_range_dict = {date: 0 for date in date_range}


        result = []
        for room_type in df['RoomType_Id'].unique():
            room_data = df.filter(pl.col('RoomType_Id') == room_type)
            hotel_id = room_data['HotelId'][0]
            room_availability = {'HotelId': hotel_id, "RoomType_Id": room_type}


            for date in date_range:
                total_value=0


                # Get the indices for columns
                sell_from_index = room_data.columns.index('SellFrom')
                sell_to_index = room_data.columns.index('SellTo')
                value_index = room_data.columns.index('Value')


                for row in room_data.iter_rows():
                    # Access columns by index
                    sell_from = row[sell_from_index]  # Assuming 'SellFrom' is the first column
                    sell_to = row[sell_to_index]    # Assuming 'SellTo' is the second column
                    value = row[value_index]      # Assuming 'Value' is the third column

                    # Compare datetime objects
                    if sell_from <= date <= sell_to:
                        total_value+=value


                # Assign total_value to the corresponding date in date_range_dict
                room_availability[str(date)] = total_value  # Store value by date


            result.append(room_availability)




        final_df = pl.DataFrame(result)
        final_df = final_df.join(rooms_df, on='RoomType_Id', how='left')
        final_df = final_df.join(hotels_df, on='HotelId', how='left')


        result_df = final_df.drop(['RoomType_Id', 'HotelId'])
        return result_df


    await main()


result_df=0


@app.route("/", methods=["GET"])
def run_update_data():
    global result_df
    asyncio.run(update_data())  # Cập nhật dữ liệu
    print('update')
    resultList = {col: result_df[col].to_list() for col in result_df.columns}
    # resultList={'2025-01-17': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '2025-01-18': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '2025-01-19': [0, 1, 0, 3, 0, 0, 0, 0, 0, 0, 0], '2025-01-20': [1, 0, 1, 1, 0, 3, 0, 1, 1, 0, 0], '2025-01-21': [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], '2025-01-22': [1, 0, 0, 1, 1, 4, 0, 0, 0, 0, 1], '2025-01-23': [0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0], '2025-01-24': [1, 0, 0, 0, 1, 3, 1, 1, 0, 0, 0], '2025-01-25': [1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1], '2025-01-26': [0, 0, 1, 0, 0, 0, 2, 0, 0, 1, 0], '2025-01-27': [0, 1, 2, 1, 0, 2, 1, 0, 0, 0, 0], '2025-01-28': [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1], '2025-01-29': [0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0], '2025-01-30': [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0], '2025-01-31': [0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0], '2025-02-01': [0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1], 'room_name': ['Luxury', 'King room with Balcony', 'Superior', 'Deluxe Double Room', 'Queen', 'Deluxe Double Room', 'King room with garden view', 'Deluxe', 'Standard', 'King room with Balcony', 'King room with garden view'], 'hotel_name': ['MG Daisy', 'Elegant Feel Inn', 'MG Daisy', 'Elegant Feel Inn', 'MG Daisy', 'Ben Thanh Inn', 'Elegant Feel Inn', 'MG Daisy', 'MG Daisy', 'Ben Thanh Inn', 'Ben Thanh Inn']}
    return render_template('index.html', resultList=resultList)


if __name__ == "__main__":
  # Nếu không có PORT thì dùng cổng mặc định 5000
    app.run(host='0.0.0.0', port=10000)
