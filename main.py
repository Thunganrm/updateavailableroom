import asyncio
import json
import requests
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import itertools
from flask import Flask, jsonify, send_file, render_template_string
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

            await page.goto("https://id.bluejaypms.com/login")
            await page.select_option("select[name='ddlLangCode']", "vi-VN")
            await page.fill("input[name='txtEmail']", "ngan.lalahouse@gmail.com")
            await page.fill("input[name='txtPassword']", "Hotelhelper@2024")
            await page.click("a#lkLogin")
            await page.wait_for_timeout(5000)

            await page.wait_for_selector("#lvHotels_lbtNameHotel_0")
            await page.click("#lvHotels_lbtNameHotel_0")
            await page.wait_for_timeout(5000)

            cookies = await page.context.cookies()
            keys_to_keep = [
                "ASP.NET_SessionId", "HtLanguage", "HtToken", "HtHotelId", "HtBaseDir"
            ]
            filtered_cookies = [cookie for cookie in cookies if cookie['name'] in keys_to_keep]

            new_ht_hotel_id_list = ["5998", "6001", "6062"]
            hotel_responses = []

            for new_ht_hotel_id in new_ht_hotel_id_list:
                for i, cookie in enumerate(filtered_cookies):
                    if cookie['name'] == 'HtHotelId':
                        filtered_cookies[i]['value'] = new_ht_hotel_id
                        break

                cookie_header = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in filtered_cookies])

                url = "https://id.bluejaypms.com/app/Room/GetRoomAvails"
                headers = {
                    "Accept": "*/*", "Accept-Encoding": "gzip, deflate, br, zstd", "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
                    "Content-Type": "application/json; charset=UTF-8", "Referer": "https://id.bluejaypms.com/app/calendar",
                    "Origin": "https://id.bluejaypms.com", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                    "Cookie": cookie_header
                }

                data = [
                    {"Action": "UpdateAvail", "RoomTypeId": "9197", "FromDate": "2024-12-15", "ToDate": "2024-12-21"},
                    {"Action": "UpdateAvail", "RoomTypeId": "9198", "FromDate": "2024-12-15", "ToDate": "2024-12-21"},
                    # Thêm các dữ liệu phòng khác
                ]

                json_data = json.dumps(data)
                response = requests.post(url, headers=headers, data=json_data)
                if response.status_code == 200:
                    hotel_responses.append(response.json())

            await browser.close()

        bt = list(itertools.chain.from_iterable(hotel_responses))

        # Dữ liệu phòng và khách sạn
        rooms_data = [
            {"RoomType_Id": "9197", "room_name": "Deluxe Double Room"},
            {"RoomType_Id": "9198", "room_name": "King room with garden view"},
            # Thêm các phòng khác
        ]
        rooms_df = pl.DataFrame(rooms_data)

        hotels_data = [
            {"HotelId": "6001", "hotel_name": "Ben Thanh Inn"},
            {"HotelId": "5998", "hotel_name": "Elegant Feel Inn"},
            {"HotelId": "6062", "hotel_name": "MG Daisy"},
        ]
        hotels_df = pl.DataFrame(hotels_data)

        df = pl.DataFrame(bt)
        print(df.columns)


        start_date = datetime.today()
        end_date = start_date + timedelta(days=6)

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
        end_date = start_date + timedelta(days=6)

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
                print(f"Checking availability for date: {date}")

                # Get the indices for columns
                sell_from_index = room_data.columns.index('SellFrom')
                sell_to_index = room_data.columns.index('SellTo')
                value_index = room_data.columns.index('Value')

                for row in room_data.iter_rows():
                    # Access columns by index
                    sell_from = row[sell_from_index]  # Assuming 'SellFrom' is the first column
                    sell_to = row[sell_to_index]    # Assuming 'SellTo' is the second column
                    value = row[value_index]      # Assuming 'Value' is the third column
                    print('sell_from',sell_from)
                    print('date',date)
                    print('sell',sell_to)
                    # Compare datetime objects
                    if sell_from <= date <= sell_to:
                        total_value+=value
                        print('total_valuet',total_value)

                # Assign total_value to the corresponding date in date_range_dict
                room_availability[str(date)] = total_value  # Store value by date

            result.append(room_availability)


        final_df = pl.DataFrame(result)
        print(final_df)
        final_df = final_df.join(rooms_df, on='RoomType_Id', how='left')
        final_df = final_df.join(hotels_df, on='HotelId', how='left')

        result_df = final_df.drop(['RoomType_Id', 'HotelId'])
        return result_df

    await main()

result_df=0

@app.route("/", methods=["GET"])
def run_update_data():
    global result_df
    print("Starting data update...",result_df)  # Log message
    try:
        asyncio.run(update_data())
        print('result_df', result_df)

        # Chuyển đổi Polars DataFrame sang Pandas DataFrame
        pandas_df = result_df.to_pandas()

        # Sử dụng .to_html() từ Pandas DataFrame
        result_html = pandas_df.to_html(classes='table table-bordered table-striped', index=False)

        return render_template_string("""
            <html>
                <head>
                    <title>Hotel Room Availability</title>
                    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
                </head>
                <body>
                    <div class="container">
                        <h2>Hotel Room Availability</h2>
                        {{ result_html|safe }}
                    </div>
                </body>
            </html>
        """, result_html=result_html)
    except Exception as e:
        return e


if __name__ == "__main__":
    app.run(debug=True)
