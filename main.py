import flet as ft
from datetime import datetime
import pytz
import httpx

def main(page: ft.Page):
    page.title = "مشاهدة المباريات"
    page.padding = 20
    page.bgcolor = "#1A1A1A"
    
    # استخدم هذا الأسلوب للإصدارات الحديثة من Flet
    page.window.width = 390
    page.window.height = 700
    
    title = ft.Text(
        "مشاهدة المباريات",
        size=24,
        weight=ft.FontWeight.BOLD,
        color="#E0E0E0",
        text_align=ft.TextAlign.CENTER
    )
    
    matches_list = ft.ListView(expand=True, spacing=16, padding=16)
    
    def show_stream_links(match):
        # تعريف صفحة روابط البث
        loading_text = ft.Text("جاري تحميل الروابط...", color="#9E9E9E")
        links_container = ft.Container(
            content=ft.Column([
                ft.Text("روابط البث:", size=16, weight=ft.FontWeight.BOLD, color="#E0E0E0"),
                ft.Row([], wrap=True, alignment=ft.MainAxisAlignment.CENTER)
            ]),
            padding=10
        )
        
        stream_links_view = ft.View(
            "/stream_links",
            [
                ft.AppBar(title=ft.Text("روابط البث"), bgcolor="#2A2A2A"),
                ft.Column([
                    ft.Text(f"{match['team1']} vs {match['team2']}", size=20, weight=ft.FontWeight.BOLD, color="#E0E0E0"),
                    ft.Text(f"البطولة: {match['tournament']}", size=16, color="#4CAF50"),
                    loading_text,
                    links_container
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ],
            bgcolor="#1A1A1A",
            padding=20
        )
        page.views.append(stream_links_view)
        page.go("/stream_links")
        
        # تحميل روابط البث
        fetch_stream_links(match['watch_Id'], loading_text, links_container)

    def fetch_stream_links(watch_id, loading_text, links_container):
        try:
            with httpx.Client() as client:
                response = client.get(f"https://spider-stirring-thrush.ngrok-free.app/stream_links/{watch_id}")
                links_data = response.json()
            
            links_row = links_container.content.controls[1]
            links_row.controls.clear()
            
            for link in links_data['links']:
                link_button = ft.ElevatedButton(
                    link['text'],
                    on_click=lambda _, url=link['href']: show_stream(url),
                    style=ft.ButtonStyle(
                        color="#FFFFFF", 
                        bgcolor="#4CAF50" if link['is_active'] else "#9E9E9E"
                    ),
                    width=100,
                    height=40
                )
                links_row.controls.append(link_button)
            
            loading_text.visible = False
            page.update()
        except Exception as ex:
            print(f"Error fetching stream links: {ex}")
            error_text = ft.Text("حدث خطأ أثناء تحميل روابط البث", color="#FF0000")
            links_container.content.controls.append(error_text)
            loading_text.visible = False
            page.update()

    def show_stream(url):
        # إنشاء صفحة جديدة لعرض البث
        stream_view = ft.View(
            "/stream",
            [
                ft.AppBar(
                    title=ft.Text("مشاهدة البث"),
                    bgcolor="#2A2A2A",
                    actions=[
                        ft.IconButton(
                            icon=ft.icons.FULLSCREEN,
                            tooltip="ملء الشاشة",
                            on_click=lambda _: toggle_fullscreen()
                        )
                    ]
                ),
                ft.WebView(
                    url=url,
                    expand=True
                )
            ],
            bgcolor="#1A1A1A",
            padding=0
        )
        page.views.append(stream_view)
        page.go("/stream")

    def toggle_fullscreen():
        page.window_full_screen = not page.window_full_screen
        page.update()

    def show_match_details(match):
        # تعريف صفحة التفاصيل
        details_view = ft.View(
            "/match_details",
            [
                ft.AppBar(title=ft.Text("تفاصيل المباراة"), bgcolor="#2A2A2A"),
                ft.Column([
                    ft.Text(f"{match['team1']} vs {match['team2']}", size=20, weight=ft.FontWeight.BOLD, color="#E0E0E0"),
                    ft.Text(f"البطولة: {match['tournament']}", size=16, color="#4CAF50"),
                    ft.Text(f"التوقيت: {match['start_time']}", size=16, color="#9E9E9E"),
                    ft.Text(f"القناة: {match['channel']}", size=16, color="#9E9E9E"),
                    ft.Text(f"المعلق: {match['commentator']}", size=16, color="#9E9E9E"),
                    ft.ElevatedButton(
                        "مشاهدة المباراة",
                        on_click=lambda _: page.launch_url(f"http://example.com/watch/{match['watch_id']}"),
                        style=ft.ButtonStyle(color="#FFFFFF", bgcolor="#4CAF50")
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ],
            bgcolor="#1A1A1A",
            padding=20
        )
        page.views.append(details_view)
        page.go("/match_details")

    def fetch_matches(e=None):
        matches_list.controls.clear()
        progress_ring = ft.ProgressRing()
        page.add(progress_ring)
        
        try:
            with httpx.Client() as client:
                response = client.get("https://spider-stirring-thrush.ngrok-free.app/matches")
                api_data = response.json()
            
            for match in api_data['matches']:
                start_time = datetime.fromisoformat(match['start_time'])
                local_tz = pytz.timezone('Asia/Riyadh')
                local_time = start_time.astimezone(local_tz)
                
                match_card = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Image(src=match['team1_logo'], width=40, height=40),
                            ft.Text(match['team1'], size=16, weight=ft.FontWeight.BOLD, color="#E0E0E0"),
                            ft.Text("vs", size=14, color="#4CAF50"),
                            ft.Text(match['team2'], size=16, weight=ft.FontWeight.BOLD, color="#E0E0E0"),
                            ft.Image(src=match['team2_logo'], width=40, height=40),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Text(local_time.strftime("%Y-%m-%d %H:%M"), size=14, color="#9E9E9E"),
                        ft.Text(match['tournament'], size=14, color="#4CAF50"),
                        ft.Text(f"القناة: {match['channel']}", size=12, color="#9E9E9E"),
                        ft.Text(f"المعلق: {match['commentator']}", size=12, color="#9E9E9E"),
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=16,
                    border_radius=8,
                    bgcolor="#2A2A2A",
                    border=ft.border.all(1, "#4CAF50"),
                    on_click=lambda _, m=match: show_stream_links(m)
                )
                matches_list.controls.append(match_card)
        except Exception as ex:
            print(f"Error fetching matches: {ex}")
            matches_list.controls.append(ft.Text("حدث خطأ أثناء تحميل المباريات", color="#E0E0E0"))
        
        page.remove(progress_ring)
        page.update()

    refresh_button = ft.IconButton(
        icon=ft.icons.REFRESH,
        icon_color="#4CAF50",
        on_click=fetch_matches,
        tooltip="تحديث المباريات"
    )

    # تعريف الصفحة الرئيسية
    home_view = ft.View(
        "/",
        [
            ft.Column([
                ft.Row([title, refresh_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                matches_list
            ], expand=True, spacing=20, alignment=ft.MainAxisAlignment.START)
        ],
        bgcolor="#1A1A1A",
        padding=20
    )

    # إضافة الصفحة الرئيسية إلى التطبيق
    page.views.append(home_view)

    # تحميل المباريات عند بدء التطبيق
    fetch_matches()

ft.app(target=main)
