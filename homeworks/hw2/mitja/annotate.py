from pathlib import Path
import flet as ft
import pandas as pd
import os
from typing import Optional
import sys
import argparse

# TODO axial coding, caps lock switches key mode, 1) shortcuts 2) edit

class DataManager:
    def __init__(self, csv_file: Path):
        self.csv_file = csv_file
        self.df = None
    
    def load_data(self):
        """Load CSV data and ensure required columns exist"""
        try:
            self.df = pd.read_csv(self.csv_file)
        except FileNotFoundError:
            self.df = self._create_sample_data()
            self.save_data()
        
        self._ensure_columns()
        return self.df
    
    def _create_sample_data(self):
        return pd.DataFrame({
            'id': [1, 2, 3],
            'query': ['Hello, how are you?', 'What is Python?', 'Explain machine learning'],
            'response': ['I am doing well, thank you!', 'Python is a programming language.', 'Machine learning is a subset of AI.'],
            'notes': ['', '', ''],
            'status': [None, None, None]
        })
    
    def _ensure_columns(self):
        if 'notes' not in self.df.columns:
            self.df['notes'] = ''
        if 'status' not in self.df.columns:
            self.df['status'] = None
        self.df['status'] = self.df['status'].astype('object')
    
    def save_data(self):
        self.df.to_csv(self.csv_file, index=False)
    
    def update_status(self, index: int, status: Optional[str]):
        self.df.at[index, 'status'] = status
        self.save_data()
    
    def update_notes(self, index: int, notes: str):
        self.df.at[index, 'notes'] = notes
        self.save_data()
    
    def get_progress_stats(self):
        total = len(self.df)
        completed = self.df['status'].isin(['pass', 'fail']).sum()
        return total, completed, completed / total if total > 0 else 0

class ThemeManager:
    def __init__(self, page: ft.Page):
        self.page = page
    
    def toggle_theme(self):
        self.page.theme_mode = (
            ft.ThemeMode.LIGHT 
            if self.page.theme_mode == ft.ThemeMode.DARK 
            else ft.ThemeMode.DARK
        )
        self.page.update()
        # Trigger chat display update to refresh colors
        if hasattr(self.page, 'route') and self.page.route == "/detail":
            self._notify_theme_change()
    
    def _notify_theme_change(self):
        """Notify that theme has changed - to be overridden by app"""
        pass
    
    def get_toggle_button(self, on_click_callback):
        return ft.IconButton(
            icon=ft.Icons.DARK_MODE if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE,
            tooltip="Toggle Light/Dark Mode (Ctrl+CMD+P)",
            on_click=on_click_callback,
        )
    
    def get_chat_colors(self):
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        return {
            'user_bg': ft.Colors.BLUE_900 if is_dark else ft.Colors.BLUE_100,
            'assistant_bg': ft.Colors.GREY_900 if is_dark else ft.Colors.GREY_100
        }

class UIComponents:
    @staticmethod
    def create_status_icon(status):
        if pd.isna(status) or status is None or status == '':
            return ft.Icon(ft.Icons.HELP_OUTLINE, color=ft.Colors.GREY)
        elif status == 'pass':
            return ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN)
        elif status == 'fail':
            return ft.Icon(ft.Icons.CANCEL, color=ft.Colors.RED)
        else:
            return ft.Icon(ft.Icons.HELP_OUTLINE, color=ft.Colors.GREY)
    
    @staticmethod
    def create_progress_bar(progress: float, completed: int, total: int, width: Optional[int] = None):
        return ft.ProgressBar(
            value=progress, width=width, expand=width is None,
            color=ft.Colors.BLUE, bgcolor=ft.Colors.GREY_200,
            tooltip=f"{completed} of {total} evaluated"
        )
    
    @staticmethod
    def create_chat_bubble(text: str, is_user: bool, colors: dict):
        bgcolor = colors['user_bg'] if is_user else colors['assistant_bg']
        margin_dict = {'left': 50, 'right': 10, 'bottom': 10} if is_user else {'left': 10, 'right': 50, 'bottom': 10}
        alignment = ft.alignment.center_right if is_user else ft.alignment.center_left
        
        return ft.Container(
            content=ft.Text(str(text), selectable=True, overflow=ft.TextOverflow.VISIBLE, expand=True),
            bgcolor=bgcolor, border_radius=15, 
            padding=ft.padding.all(15), margin=ft.margin.only(**margin_dict),
            alignment=alignment, expand=True,
        )
    
    @staticmethod
    def create_action_buttons(callbacks: dict):
        return [
            ft.ElevatedButton("Pass", icon=ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, 
                            bgcolor=ft.Colors.GREEN, on_click=callbacks['pass']),
            ft.ElevatedButton("Fail", icon=ft.Icons.CANCEL, color=ft.Colors.WHITE, 
                            bgcolor=ft.Colors.RED, on_click=callbacks['fail']),
            ft.OutlinedButton("Clear", icon=ft.Icons.CLEAR, on_click=callbacks['clear']),
        ]

class KeyboardHandler:
    def __init__(self, callbacks: dict):
        self.callbacks = callbacks
        self.shortcuts = {
            ("Arrow Left", "J"): 'navigate_prev',
            ("Arrow Right", "L"): 'navigate_next',
            ("K",): 'set_pass',
            ("I",): 'set_fail',
            ("M",): 'clear_status',
            ("O",): 'go_overview',
            ("P",): 'toggle_theme'
        }
    
    def handle_event(self, e: ft.KeyboardEvent, current_route: str):
        if not (e.ctrl and current_route == "/detail"):
            return
            
        for keys, action in self.shortcuts.items():
            if e.key in keys and action in self.callbacks:
                self.callbacks[action]()
                break

class ChatbotEvaluationTool:
    def __init__(self, csv_file: Path = "sample_results.csv"):
        self.data_manager = DataManager(csv_file)
        self.current_index = 0
        self.page = None
        
        # UI components
        self.notes_field = None
        self.chat_container = None
        self.overview_list = None
        
        # Managers
        self.theme_manager = None
        self.keyboard_handler = None
        
    def initialize(self, page: ft.Page):
        self.page = page
        self.theme_manager = ThemeManager(page)
        # Override the theme change notification
        self.theme_manager._notify_theme_change = self.on_theme_change
        self.keyboard_handler = KeyboardHandler({
            'navigate_prev': self.navigate_prev,
            'navigate_next': self.navigate_next,
            'set_pass': lambda: self.set_status('pass'),
            'set_fail': lambda: self.set_status('fail'),
            'clear_status': lambda: self.set_status(None),
            'go_overview': self.go_to_overview,
            'toggle_theme': lambda: self.theme_manager.toggle_theme()
        })
        self.data_manager.load_data()
    
    def on_theme_change(self):
        """Handle theme change - update chat display to refresh colors"""
        if hasattr(self, 'chat_container') and self.chat_container:
            self.update_chat_display()

    def truncate_text(self, text, max_length=50):
        return text if len(text) <= max_length else text[:max_length] + "..."
    
    def set_status(self, status):
        if self.current_index < len(self.data_manager.df):
            self.data_manager.update_status(self.current_index, status)
            self.update_overview_list()
            self.update_sidebar_status_and_progress()
            self.page.update()
    
    def on_notes_change(self, e):
        if self.current_index < len(self.data_manager.df):
            self.data_manager.update_notes(self.current_index, e.control.value)
            self.update_overview_list()
    
    def handle_keyboard_shortcuts(self, e: ft.KeyboardEvent):
        self.keyboard_handler.handle_event(e, self.page.route)
        
    def create_chat_bubble(self, text, is_user=True):
        colors = self.theme_manager.get_chat_colors()
        return UIComponents.create_chat_bubble(text, is_user, colors)
    
    def navigate_prev(self):
        """Navigate to previous conversation"""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_chat_display()
    
    def navigate_next(self):
        """Navigate to next conversation"""
        if self.current_index < len(self.data_manager.df) - 1:
            self.current_index += 1
            self.update_chat_display()
    
    def go_to_overview(self):
        """Navigate back to overview"""
        self.page.go("/overview")
        self.update_overview_list()
    
    def open_detail_view(self, index):
        """Open detail view for specific conversation"""
        self.current_index = index
        self.page.go("/detail")
        self.update_chat_display()
    
    def update_overview_list(self):
        """Update the overview list with current data"""
        if not self.overview_list:
            return
            
        self.overview_list.controls.clear()
        
        for index, row in self.data_manager.df.iterrows():
            query_preview = self.truncate_text(str(row['query']))
            notes_preview = self.truncate_text(str(row['notes']) if pd.notna(row['notes']) else "")
            
            list_tile = ft.ListTile(
                leading=UIComponents.create_status_icon(row['status']),
                title=ft.Text(f"#{row['id']}: {query_preview}", weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(f"Notes: {notes_preview}" if notes_preview else "No notes"),
                on_click=lambda e, idx=index: self.open_detail_view(idx),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST if index % 2 == 0 else None,
            )
            self.overview_list.controls.append(list_tile)
        
        if self.page:
            self.page.on_keyboard_event = self.handle_keyboard_shortcuts
            self.page.update()
    
    def update_sidebar_status_and_progress(self):
        """Update status icon and progress bar in detail view sidebar"""
        if not hasattr(self, 'detail_view') or not self.detail_view:
            return
            
        # Find the sidebar in detail view
        try:
            sidebar = self.detail_view.controls[1].controls[1]
            
            # Update status icon
            current_status = self.data_manager.df.iloc[self.current_index]['status']
            status_icon = UIComponents.create_status_icon(current_status)
            sidebar.content.controls[0].controls[1] = status_icon
            
            # Update progress
            total, completed, progress = self.data_manager.get_progress_stats()
            
            progress_bar = sidebar.content.controls[2]
            progress_bar.value = progress
            progress_bar.tooltip = f"{completed} of {total} evaluated"
            
            progress_text = sidebar.content.controls[3]
            progress_text.value = f"{completed} of {total} evaluated"
        except (IndexError, AttributeError):
            pass  # Sidebar not yet created or structure changed
    
    def update_chat_display(self):
        """Update the chat display with current conversation"""
        if self.current_index >= len(self.data_manager.df) or not self.chat_container:
            return
            
        row = self.data_manager.df.iloc[self.current_index]
        self.chat_container.controls.clear()
        
        # Create chat bubbles
        query_bubble = self.create_chat_bubble(row['query'], is_user=True)
        response_bubble = self.create_chat_bubble(row['response'], is_user=False)
        
        self.chat_container.controls.extend([
            ft.Row([ft.Container(), query_bubble], alignment=ft.MainAxisAlignment.END),
            ft.Row([response_bubble, ft.Container()], alignment=ft.MainAxisAlignment.START),
        ])
        
        # Update notes field
        if self.notes_field:
            notes = row['notes'] if pd.notna(row['notes']) else ""
            self.notes_field.value = str(notes)
        
        self.update_sidebar_status_and_progress()
        
        # Update page title
        if hasattr(self, 'detail_view') and self.detail_view and self.detail_view.appbar:
            self.detail_view.appbar.title = ft.Text(
                f"Evaluation - #{row['id']} ({self.current_index + 1}/{len(self.data_manager.df)})"
            )
        
        if self.page:
            self.page.on_keyboard_event = self.handle_keyboard_shortcuts
            self.page.update()
            self.chat_container.scroll_to(0, duration=0)
    
    def create_overview_page(self):
        """Create the overview page with list of all conversations"""
        self.overview_list = ft.ListView(expand=True, spacing=5, padding=ft.padding.all(10))
        self.update_overview_list()
        
        total, completed, progress = self.data_manager.get_progress_stats()
        progress_bar = UIComponents.create_progress_bar(progress, completed, total)

        self.overview_view = ft.View(
            "/overview",
            [
                ft.AppBar(
                    title=ft.Text("Chatbot Trace Evaluation - Overview"),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    actions=[self.theme_manager.get_toggle_button(lambda e: self.theme_manager.toggle_theme())],
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            progress_bar,
                            ft.Text(f"{completed} of {total} evaluated", size=12, color=ft.Colors.GREY),
                        ], spacing=20, alignment=ft.MainAxisAlignment.START),
                        self.overview_list,
                    ], expand=True, spacing=20),
                    expand=True,
                    padding=ft.padding.all(10),
                )
            ],
        )
        
        return self.overview_view
    
    def create_detail_page(self):
        """Create the detailed evaluation page"""
        self.chat_container = ft.ListView(expand=True, spacing=10, padding=ft.padding.all(10))
        
        self.notes_field = ft.TextField(label="Notes",
            multiline=True, min_lines=4, max_lines=6,
            on_change=self.on_notes_change,
            autofocus=True,
        )
        
        # Create action buttons using UIComponents
        action_buttons = UIComponents.create_action_buttons({
            'pass': lambda e: self.set_status('pass'),
            'fail': lambda e: self.set_status('fail'),
            'clear': lambda e: self.set_status(None)
        })
        
        # Navigation buttons
        nav_buttons = [
            ft.IconButton(icon=ft.Icons.ARROW_BACK, tooltip="Previous (Ctrl+Left)", 
                         on_click=lambda e: self.navigate_prev()),
            ft.IconButton(icon=ft.Icons.ARROW_FORWARD, tooltip="Next (Ctrl+Right)", 
                         on_click=lambda e: self.navigate_next()),
            ft.IconButton(icon=ft.Icons.LIST, tooltip="Overview (Ctrl+O)", 
                         on_click=lambda e: self.go_to_overview()),
        ]
        
        # Sidebar
        total, completed, progress = self.data_manager.get_progress_stats()
        progress_bar = UIComponents.create_progress_bar(progress, completed, total, width=260)
        
        current_status = None
        if self.current_index < len(self.data_manager.df):
            current_status = self.data_manager.df.iloc[self.current_index]['status']
        status_icon = UIComponents.create_status_icon(current_status)

        try:
            with open('shortcuts.svg', 'r') as f:
                shortcuts_svg = f.read()
        except FileExistsError:
            shortcuts_svg = ""

        shortcuts = ft.Container(
            content=ft.Column([
            ft.Text("Keyboard Shortcuts (CTRL+CMD+)", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY),
            ft.Container(
                content=ft.Image(src=shortcuts_svg, width=150, height=150),
                alignment=ft.alignment.center,
            ),
            ], spacing=5),
            margin=ft.margin.only(top=10),
        )

        sidebar = ft.Container(
            width=300,
            content=ft.Column([
                ft.Row([ft.Text("Evaluation", size=20, weight=ft.FontWeight.BOLD), status_icon], 
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                progress_bar,
                ft.Text(f"{completed} of {total} evaluated", size=12, color=ft.Colors.GREY),
                self.notes_field,
                ft.Row(action_buttons),
                ft.Divider(),
                ft.Text("Navigation", size=16, weight=ft.FontWeight.BOLD),
                ft.Row(nav_buttons),
                shortcuts,
            ], spacing=10),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        )
        
        main_content = ft.Container(content=self.chat_container, expand=True, padding=ft.padding.all(10))
        
        self.detail_view = ft.View(
            "/detail",
            [
                ft.AppBar(
                    title=ft.Text("Chatbot Trace Evaluation - Detail"),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    actions=[self.theme_manager.get_toggle_button(lambda e: self.theme_manager.toggle_theme())],
                ),
                ft.Row([main_content, sidebar], expand=True)
            ],
        )
        
        return self.detail_view
    
    def route_change(self, route):
        """Handle route changes"""
        self.page.views.clear()
        
        if self.page.route == "/overview":
            self.page.views.append(self.create_overview_page())
        elif self.page.route == "/detail":
            self.page.views.append(self.create_detail_page())
            self.update_chat_display()
        
        self.page.on_keyboard_event = self.handle_keyboard_shortcuts
        self.page.update()
    
    def view_pop(self, view):
        """Handle view pop (back button)"""
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)

def parse_args():
    parser = argparse.ArgumentParser(description="Chatbot Trace Evaluation Tool")
    parser.add_argument(
        "--csv-file",
        type=Path,
        default=Path("sample_results.csv"),
        help="Path to the CSV file to use for evaluation"
    )
    # Check for help flag before parsing known args
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        parser.print_help()
        sys.exit(0)
    args, _ = parser.parse_known_args()
    return args

def main(page: ft.Page):
    """Main application entry point"""
    args = parse_args()
    
    # Initialize the evaluation tool
    eval_tool = ChatbotEvaluationTool(csv_file=args.csv_file)
    eval_tool.initialize(page)
    
    # Configure page
    page.title = "Chatbot Trace Evaluation Tool"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 800
    page.window.height = 700
    
    # Set up routing
    page.on_route_change = eval_tool.route_change
    page.on_view_pop = eval_tool.view_pop
    page.on_keyboard_event = eval_tool.handle_keyboard_shortcuts
    
    # Start with overview
    page.go("/overview")

if __name__ == "__main__":
    ft.app(target=main)