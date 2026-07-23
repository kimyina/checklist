#!/usr/bin/env python3
import ctypes
import os
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gio, GLib, Gtk


APP_ID = "io.github.kimyina.checklist"
WEEKDAYS_KO = ("월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일")
FONT_PATH = Path(__file__).resolve().parent / "assets" / "fonts" / "Pretendard-Regular.otf"


def register_bundled_font():
    """Make the bundled Pretendard available only to this app process."""
    if not FONT_PATH.is_file():
        return False

    try:
        fontconfig = ctypes.CDLL("libfontconfig.so.1")
        fontconfig.FcConfigGetCurrent.restype = ctypes.c_void_p
        fontconfig.FcConfigAppFontAddFile.argtypes = (ctypes.c_void_p, ctypes.c_char_p)
        fontconfig.FcConfigAppFontAddFile.restype = ctypes.c_int
        config = fontconfig.FcConfigGetCurrent()
        if not config:
            return False
        return bool(fontconfig.FcConfigAppFontAddFile(config, os.fsencode(FONT_PATH)))
    except (AttributeError, OSError):
        return False


register_bundled_font()


CSS = b"""
* {
  font-family: Pretendard, sans-serif;
  font-size: 10pt;
}
window {
  background: @theme_bg_color;
  color: @theme_fg_color;
}
.topbar {
  background: @theme_bg_color;
  border-bottom: 1px solid @borders;
  padding: 5px 7px;
}
.app-title, .date-title {
  font-weight: 600;
}
.calendar-wrap {
  padding: 0 10px;
}
.calendar-shell {
  background: @theme_bg_color;
  border: 1px solid @borders;
  border-radius: 4px;
}
.calendar-header {
  padding: 2px 3px 0 3px;
}
.calendar-title {
  font-weight: 600;
}
.calendar-nav,
.calendar-nav:focus {
  background: transparent;
  border: 0;
  border-radius: 999px;
  box-shadow: none;
  outline-color: transparent;
  padding: 0;
  min-width: 24px;
  min-height: 24px;
}
.calendar-nav:hover {
  background-color: alpha(@theme_fg_color, 0.07);
}
.calendar-weekdays {
  padding: 1px 4px 0 4px;
}
.calendar-weekday {
  color: alpha(@theme_fg_color, 0.45);
}
.calendar-grid {
  padding: 0 4px 3px 4px;
}
.calendar-day,
.calendar-day:focus {
  color: @theme_fg_color;
  background: transparent;
  border: 0;
  border-radius: 999px;
  box-shadow: none;
  outline-color: transparent;
  margin: 4px 4px;
  padding: 0;
  min-height: 25px;
}
.calendar-day:hover {
  background-color: alpha(@theme_fg_color, 0.07);
}
.calendar-day.today {
  color: @theme_fg_color;
  background-color: alpha(@theme_fg_color, 0.18);
  border: 1px solid alpha(@theme_fg_color, 0.42);
  font-weight: 700;
}
.calendar-day.has-tasks {
  font-weight: 700;
  box-shadow: inset 0 -2px alpha(@theme_fg_color, 0.42);
}
.calendar-day.other-month {
  color: alpha(@theme_fg_color, 0.20);
}
.task-list,
.task-list:focus {
  background: @theme_bg_color;
  border: 0;
  padding: 5px 4px;
  outline-color: transparent;
  box-shadow: none;
}
.task-row,
.task-row:hover,
.task-row:focus,
.task-row:selected,
.task-row:focus:selected {
  color: @theme_fg_color;
  background: transparent;
  padding: 3px 5px 3px 7px;
  border: 0;
  outline-color: transparent;
  box-shadow: none;
}
.task-row.reordering {
  color: @theme_fg_color;
  background-color: @theme_bg_color;
  border: 1px solid alpha(@theme_fg_color, 0.13);
  border-radius: 7px;
  margin: 3px 6px;
  padding: 2px 6px;
  box-shadow: 0 7px 16px rgba(0, 0, 0, 0.24);
}
.task-row.reordering .task-text,
.task-row.reordering .task-text text,
.task-row.reordering .task-text text:focus,
.task-row.reordering .task-detail-text,
.task-row.reordering .task-detail-text text,
.task-row.reordering .task-detail-text text:focus {
  background-color: @theme_bg_color;
}
.task-text,
.task-text:focus,
.task-detail-text,
.task-detail-text:focus {
  background: transparent;
  border: 0;
  padding: 6px 3px;
  outline-color: transparent;
  box-shadow: none;
}
.task-text text,
.task-detail-text text {
  color: @theme_fg_color;
  background: transparent;
}
.task-text text:focus,
.task-detail-text text:focus {
  color: @theme_fg_color;
  background-color: alpha(@theme_fg_color, 0.055);
  border-color: transparent;
  outline-color: transparent;
  box-shadow: none;
}
.task-text text:selected,
.task-text text:focus:selected,
.task-detail-text text:selected,
.task-detail-text text:focus:selected,
.task-list selection {
  color: @theme_fg_color;
  background-color: alpha(@theme_fg_color, 0.10);
  outline-color: transparent;
}
.task-details {
  background: transparent;
}
.task-detail-row {
  color: @theme_fg_color;
  background: transparent;
  border: 0;
  padding: 0;
}
.task-detail-row.reordering {
  background-color: @theme_bg_color;
  border: 1px solid alpha(@theme_fg_color, 0.13);
  border-radius: 7px;
  margin: 2px 4px;
  padding: 0 3px;
  box-shadow: 0 5px 12px rgba(0, 0, 0, 0.22);
}
.task-detail-spacer {
  min-width: 14px;
}
.task-detail-marker {
  color: alpha(@theme_fg_color, 0.45);
  padding: 6px 1px 0 0;
}
.task-row checkbutton,
.task-row checkbutton:focus,
.task-row checkbutton check:focus {
  padding: 0;
  margin: 0;
  outline-color: transparent;
  box-shadow: none;
}
.task-row checkbutton check {
  min-width: 11px;
  min-height: 11px;
  padding: 0;
  margin: 0 2px 0 0;
  -gtk-icon-transform: scale(0.72);
}
.addbar {
  background: @theme_bg_color;
  padding: 5px 8px 7px 7px;
  border-top: 1px solid @borders;
}
.composer-arrow {
  color: alpha(@theme_fg_color, 0.28);
  padding: 6px 5px 0 2px;
}
.composer {
  background: transparent;
  border: 0;
  padding: 4px 2px;
}
.composer:focus,
.composer text:focus {
  background: transparent;
  border-color: transparent;
  outline-color: transparent;
  box-shadow: none;
}
.composer text {
  color: @theme_fg_color;
  background: transparent;
}
.composer text:selected,
.composer text:focus:selected {
  color: @theme_fg_color;
  background-color: alpha(@theme_fg_color, 0.10);
}
.composer-hint {
  color: alpha(@theme_fg_color, 0.50);
}
.empty-label {
  color: alpha(@theme_fg_color, 0.55);
  padding: 28px 10px;
}
"""


def data_directory():
    base = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    path = os.path.join(base, "daily-checklist")
    os.makedirs(path, exist_ok=True)
    return path


class ChecklistDatabase:
    def __init__(self):
        self.connection = sqlite3.connect(os.path.join(data_directory(), "checklist.db"))
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_date TEXT NOT NULL,
                position INTEGER NOT NULL,
                text TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS task_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                position INTEGER NOT NULL,
                text TEXT NOT NULL DEFAULT '',
                FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
            """
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_task_details_task "
            "ON task_details(task_id, position)"
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_tasks_date ON tasks(task_date, position)"
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS app_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    def tasks_for(self, selected_date):
        return self.connection.execute(
            "SELECT id, text, completed FROM tasks WHERE task_date = ? ORDER BY position, id",
            (selected_date.isoformat(),),
        ).fetchall()

    def add(self, selected_date, text):
        position = self.connection.execute(
            "SELECT COALESCE(MAX(position), -1) + 1 FROM tasks WHERE task_date = ?",
            (selected_date.isoformat(),),
        ).fetchone()[0]
        cursor = self.connection.execute(
            "INSERT INTO tasks(task_date, position, text, completed) VALUES (?, ?, ?, 0)",
            (selected_date.isoformat(), position, text),
        )
        self.connection.commit()
        return cursor.lastrowid

    def update_text(self, task_id, text):
        self.connection.execute("UPDATE tasks SET text = ? WHERE id = ?", (text, task_id))
        self.connection.commit()

    def details_for(self, task_id):
        return self.connection.execute(
            "SELECT id, text FROM task_details "
            "WHERE task_id = ? ORDER BY position, id",
            (task_id,),
        ).fetchall()

    def add_detail(self, task_id, text=""):
        position = self.connection.execute(
            "SELECT COALESCE(MAX(position), -1) + 1 "
            "FROM task_details WHERE task_id = ?",
            (task_id,),
        ).fetchone()[0]
        cursor = self.connection.execute(
            "INSERT INTO task_details(task_id, position, text) VALUES (?, ?, ?)",
            (task_id, position, text),
        )
        self.connection.commit()
        return cursor.lastrowid

    def update_detail_text(self, detail_id, text):
        self.connection.execute(
            "UPDATE task_details SET text = ? WHERE id = ?", (text, detail_id)
        )
        self.connection.commit()

    def delete_detail(self, detail_id):
        self.connection.execute("DELETE FROM task_details WHERE id = ?", (detail_id,))
        self.connection.commit()

    def update_detail_positions(self, detail_ids):
        for position, detail_id in enumerate(detail_ids):
            self.connection.execute(
                "UPDATE task_details SET position = ? WHERE id = ?",
                (position, detail_id),
            )
        self.connection.commit()

    def update_completed(self, task_id, completed):
        self.connection.execute(
            "UPDATE tasks SET completed = ? WHERE id = ?", (int(completed), task_id)
        )
        self.connection.commit()

    def delete(self, task_id):
        self.connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.connection.commit()

    def update_positions(self, task_ids):
        for position, task_id in enumerate(task_ids):
            self.connection.execute(
                "UPDATE tasks SET position = ? WHERE id = ?", (position, task_id)
            )
        self.connection.commit()

    def task_dates_between(self, start_date, end_date):
        rows = self.connection.execute(
            "SELECT DISTINCT task_date FROM tasks WHERE task_date BETWEEN ? AND ?",
            (start_date.isoformat(), end_date.isoformat()),
        ).fetchall()
        return {date.fromisoformat(row[0]) for row in rows}

    def marked_days(self, year, month):
        prefix = f"{year:04d}-{month:02d}-%"
        rows = self.connection.execute(
            "SELECT DISTINCT CAST(substr(task_date, 9, 2) AS INTEGER) "
            "FROM tasks WHERE task_date LIKE ?",
            (prefix,),
        ).fetchall()
        return [row[0] for row in rows]

    def get_window_position(self):
        row = self.connection.execute(
            "SELECT value FROM app_state WHERE key = 'window_position'"
        ).fetchone()
        if row is None:
            return None
        try:
            x, y = (int(value) for value in row[0].split(",", 1))
            return x, y
        except (TypeError, ValueError):
            return None

    def set_window_position(self, x, y):
        self.connection.execute(
            "INSERT OR REPLACE INTO app_state(key, value) VALUES ('window_position', ?)",
            (f"{int(x)},{int(y)}",),
        )
        self.connection.commit()

    def get_window_size(self):
        row = self.connection.execute(
            "SELECT value FROM app_state WHERE key = 'window_size'"
        ).fetchone()
        if row is None:
            return None
        try:
            width, height = (int(value) for value in row[0].split(",", 1))
            return max(310, width), max(280, height)
        except (TypeError, ValueError):
            return None

    def set_window_geometry(self, x, y, width, height):
        self.connection.executemany(
            "INSERT OR REPLACE INTO app_state(key, value) VALUES (?, ?)",
            (
                ("window_position", f"{int(x)},{int(y)}"),
                ("window_size", f"{int(width)},{int(height)}"),
            ),
        )
        self.connection.commit()

    def close(self):
        self.connection.close()


class DailyChecklistWindow(Gtk.ApplicationWindow):
    def __init__(self, application):
        super().__init__(application=application, title="checklist")
        self.set_size_request(310, 280)
        self.set_resizable(True)
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            self.set_icon_from_file(icon_path)
        self.db = ChecklistDatabase()
        self.set_default_size(*(self.db.get_window_size() or (310, 280)))
        saved_position = self.db.get_window_position()
        self._geometry_saved = False
        if saved_position is None:
            self.set_position(Gtk.WindowPosition.CENTER)
        else:
            self.move(*saved_position)
        self.selected_date = date.today()
        self._loading_rows = False
        self._undo_histories = {}
        self._reorder_row = None
        self._reorder_view = None
        self._detail_reorder_item = None
        self._detail_reorder_view = None
        self._detail_reorder_parent = None
        self._desktop_interface_settings = None

        self.connect("delete-event", self.on_delete_event)
        self.connect("destroy", self.on_destroy)
        self.connect("key-press-event", self.on_key_press)

        gtk_settings = Gtk.Settings.get_default()
        self.configure_theme_preference(gtk_settings)

        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        gtk_settings.set_property("gtk-cursor-blink", False)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(160)
        self.add(self.stack)

        self.calendar_page = self.build_calendar_page()
        self.checklist_page = self.build_checklist_page()
        self.stack.add_named(self.calendar_page, "calendar")
        self.stack.add_named(self.checklist_page, "checklist")
        self.stack.set_visible_child_name("calendar")

    def configure_theme_preference(self, gtk_settings):
        schema_source = Gio.SettingsSchemaSource.get_default()
        if schema_source is None:
            return

        schema = schema_source.lookup("org.gnome.desktop.interface", True)
        if schema is None or not schema.has_key("color-scheme"):
            return

        self._desktop_interface_settings = Gio.Settings.new_full(schema, None, None)

        def sync_dark_preference(*_args):
            color_scheme = self._desktop_interface_settings.get_string("color-scheme")
            gtk_settings.set_property(
                "gtk-application-prefer-dark-theme",
                color_scheme == "prefer-dark",
            )

        self._desktop_interface_settings.connect(
            "changed::color-scheme", sync_dark_preference
        )
        sync_dark_preference()

    def build_calendar_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.get_style_context().add_class("calendar-wrap")

        shell = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        shell.set_vexpand(True)
        shell.get_style_context().add_class("calendar-shell")

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header.get_style_context().add_class("calendar-header")
        previous_button = Gtk.Button()
        previous_button.set_relief(Gtk.ReliefStyle.NONE)
        previous_button.set_can_focus(False)
        previous_button.get_style_context().add_class("calendar-nav")
        previous_button.add(
            Gtk.Image.new_from_icon_name("go-previous-symbolic", Gtk.IconSize.MENU)
        )
        previous_button.connect("clicked", self.shift_calendar_month, -1)
        header.pack_start(previous_button, False, False, 0)

        self.calendar_title = Gtk.Label()
        self.calendar_title.get_style_context().add_class("calendar-title")
        header.pack_start(self.calendar_title, True, True, 0)

        next_button = Gtk.Button()
        next_button.set_relief(Gtk.ReliefStyle.NONE)
        next_button.set_can_focus(False)
        next_button.get_style_context().add_class("calendar-nav")
        next_button.add(
            Gtk.Image.new_from_icon_name("go-next-symbolic", Gtk.IconSize.MENU)
        )
        next_button.connect("clicked", self.shift_calendar_month, 1)
        header.pack_end(next_button, False, False, 0)
        shell.pack_start(header, False, False, 0)

        weekdays = Gtk.Grid(column_homogeneous=True)
        weekdays.get_style_context().add_class("calendar-weekdays")
        for column, name in enumerate(("일", "월", "화", "수", "목", "금", "토")):
            label = Gtk.Label(label=name)
            label.get_style_context().add_class("calendar-weekday")
            weekdays.attach(label, column, 0, 1, 1)
        shell.pack_start(weekdays, False, False, 0)

        self.calendar_grid = Gtk.Grid(column_homogeneous=True, row_homogeneous=True)
        self.calendar_grid.set_vexpand(True)
        self.calendar_grid.get_style_context().add_class("calendar-grid")
        shell.pack_start(self.calendar_grid, True, True, 0)
        content.pack_start(shell, True, True, 0)
        page.pack_start(content, True, True, 0)

        today = date.today()
        self.calendar_year = today.year
        self.calendar_month = today.month
        self.calendar_day_buttons = {}
        self.render_calendar()
        return page

    def shift_calendar_month(self, _button, offset):
        month_index = self.calendar_year * 12 + self.calendar_month - 1 + offset
        self.calendar_year, zero_based_month = divmod(month_index, 12)
        self.calendar_month = zero_based_month + 1
        self.render_calendar()

    def render_calendar(self):
        if not hasattr(self, "calendar_grid"):
            return
        for child in self.calendar_grid.get_children():
            self.calendar_grid.remove(child)

        self.calendar_title.set_text(f"{self.calendar_year}년 {self.calendar_month}월")
        first_of_month = date(self.calendar_year, self.calendar_month, 1)
        days_after_sunday = (first_of_month.weekday() + 1) % 7
        grid_start = first_of_month - timedelta(days=days_after_sunday)
        grid_end = grid_start + timedelta(days=41)
        task_dates = self.db.task_dates_between(grid_start, grid_end)
        today = date.today()
        self.calendar_day_buttons = {}

        for index in range(42):
            current_date = grid_start + timedelta(days=index)
            button = Gtk.Button(label=str(current_date.day))
            button.set_relief(Gtk.ReliefStyle.NONE)
            button.set_can_focus(False)
            context = button.get_style_context()
            context.add_class("calendar-day")
            if current_date.month != self.calendar_month:
                context.add_class("other-month")
            if current_date == today:
                context.add_class("today")
            if current_date in task_dates:
                context.add_class("has-tasks")
            button.connect("clicked", self.on_calendar_date_clicked, current_date)
            self.calendar_grid.attach(button, index % 7, index // 7, 1, 1)
            self.calendar_day_buttons[current_date] = button
        self.calendar_grid.show_all()

    def on_calendar_date_clicked(self, _button, selected_date):
        if self.stack.get_visible_child_name() != "calendar":
            return
        self.selected_date = selected_date
        self.calendar_year = selected_date.year
        self.calendar_month = selected_date.month
        self.show_checklist()

    def build_checklist_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        header.get_style_context().add_class("topbar")
        back_button = Gtk.Button()
        back_button.set_relief(Gtk.ReliefStyle.NONE)
        back_button.set_tooltip_text("달력으로 돌아가기 (Esc)")
        back_button.add(Gtk.Image.new_from_icon_name("go-previous-symbolic", Gtk.IconSize.BUTTON))
        back_button.connect("clicked", lambda _button: self.show_calendar())
        header.pack_start(back_button, False, False, 0)

        self.date_label = Gtk.Label(xalign=0)
        self.date_label.get_style_context().add_class("date-title")
        header.pack_start(self.date_label, True, True, 2)
        page.pack_start(header, False, False, 0)

        self.task_list = Gtk.ListBox()
        self.task_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.task_list.set_sort_func(self.sort_task_rows)
        self.task_list.get_style_context().add_class("task-list")

        self.empty_label = Gtk.Label(label="아직 적어 둔 할 일이 없습니다")
        self.empty_label.get_style_context().add_class("empty-label")

        list_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        list_container.pack_start(self.empty_label, False, False, 0)
        list_container.pack_start(self.task_list, False, False, 0)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.add_with_viewport(list_container)
        page.pack_start(scroller, True, True, 0)

        addbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        addbar.get_style_context().add_class("addbar")
        self.composer_arrow = Gtk.Label(label="→")
        self.composer_arrow.set_yalign(0)
        self.composer_arrow.get_style_context().add_class("composer-arrow")
        addbar.pack_start(self.composer_arrow, False, False, 0)
        self.new_task_view = Gtk.TextView()
        self.new_task_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.new_task_view.set_accepts_tab(False)
        self.new_task_view.set_size_request(-1, 30)
        self.new_task_view.get_style_context().add_class("composer")
        self.new_task_view.connect("key-press-event", self.on_composer_key_press)
        self.new_task_buffer = self.new_task_view.get_buffer()
        self.register_undo_buffer(self.new_task_buffer)
        addbar.pack_start(self.new_task_view, True, True, 0)
        page.pack_end(addbar, False, False, 0)
        return page

    def show_checklist(self):
        weekday = WEEKDAYS_KO[self.selected_date.weekday()]
        self.date_label.set_text(
            f"{self.selected_date.month}월 {self.selected_date.day}일 {weekday}"
        )
        self.load_tasks()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
        self.stack.set_visible_child_name("checklist")

    def show_calendar(self):
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
        self.stack.set_visible_child_name("calendar")
        self.refresh_calendar_marks()

    def refresh_calendar_marks(self, *_args):
        self.render_calendar()
        return False

    def load_tasks(self):
        self._loading_rows = True
        for child in self.task_list.get_children():
            self.unregister_undo_buffer(child.task_view.get_buffer())
            for detail_item in child.detail_box.get_children():
                self.unregister_undo_buffer(detail_item.detail_view.get_buffer())
            self.task_list.remove(child)
        for task_id, text, completed in self.db.tasks_for(self.selected_date):
            row = self.append_task_row(task_id, text, bool(completed))
            for detail_id, detail_text in self.db.details_for(task_id):
                self.append_detail_row(row, detail_id, detail_text)
        self._loading_rows = False
        self.update_empty_state()
        self.task_list.show_all()

    def append_task_row(self, task_id, text, completed=False):
        row = Gtk.ListBoxRow()
        row.task_id = task_id
        row.sort_position = max(
            (child.sort_position for child in self.task_list.get_children()), default=-1
        ) + 1
        row.set_activatable(False)
        row.set_selectable(False)
        row.get_style_context().add_class("task-row")
        group = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)

        check = Gtk.CheckButton()
        check.set_active(completed)
        check.set_tooltip_text("완료")
        main_box.pack_start(check, False, False, 0)

        task_view = Gtk.TextView()
        task_view.set_editable(True)
        task_view.set_cursor_visible(True)
        task_view.set_can_focus(True)
        task_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        task_view.set_accepts_tab(False)
        task_view.set_hexpand(True)
        task_view.set_size_request(-1, 34)
        task_view.get_style_context().add_class("task-text")
        task_buffer = task_view.get_buffer()
        task_buffer.set_text(text)
        task_buffer.create_tag("completed", strikethrough=True)
        self.register_undo_buffer(task_buffer)
        main_box.pack_start(task_view, True, True, 0)

        detail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        detail_box.get_style_context().add_class("task-details")
        group.pack_start(main_box, False, False, 0)
        group.pack_start(detail_box, False, False, 0)

        row.add(group)
        self.task_list.add(row)
        row.task_view = task_view
        row.check_button = check
        row.detail_box = detail_box
        row.completed = completed
        self.set_row_completed_style(row, completed)

        check.connect("toggled", self.on_task_toggled, task_id, row)
        task_buffer.connect("changed", self.on_task_text_changed, task_id, row)
        task_view.add_events(
            Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK
        )
        task_view.connect("key-press-event", self.on_task_key_press)
        task_view.connect("button-press-event", self.on_task_middle_press, row)
        task_view.connect_after("button-press-event", self.on_task_edit_click)
        task_view.connect("motion-notify-event", self.on_task_reorder_motion, row)
        task_view.connect("button-release-event", self.on_task_reorder_release, row)
        task_view.connect("populate-popup", self.on_task_populate_popup, task_id, row)
        return row

    def append_detail_row(self, row, detail_id, text=""):
        item = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        item.detail_id = detail_id
        item.sort_position = len(row.detail_box.get_children())
        item.get_style_context().add_class("task-detail-row")

        spacer = Gtk.Box()
        spacer.get_style_context().add_class("task-detail-spacer")
        item.pack_start(spacer, False, False, 0)

        marker = Gtk.Label(label="ㄴ")
        marker.set_yalign(0)
        marker.get_style_context().add_class("task-detail-marker")
        item.pack_start(marker, False, False, 0)

        detail_view = Gtk.TextView()
        detail_view.set_editable(True)
        detail_view.set_cursor_visible(True)
        detail_view.set_can_focus(True)
        detail_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        detail_view.set_accepts_tab(False)
        detail_view.set_hexpand(True)
        detail_view.set_size_request(-1, 30)
        detail_view.get_style_context().add_class("task-detail-text")
        detail_buffer = detail_view.get_buffer()
        detail_buffer.set_text(text)
        detail_buffer.create_tag("completed", strikethrough=True)
        self.register_undo_buffer(detail_buffer)
        item.pack_start(detail_view, True, True, 0)

        item.detail_view = detail_view
        row.detail_box.pack_start(item, False, False, 0)
        self.set_buffer_completed_style(detail_buffer, row.completed)

        detail_buffer.connect(
            "changed", self.on_detail_text_changed, detail_id, row, item
        )
        detail_view.add_events(
            Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK
        )
        detail_view.connect("key-press-event", self.on_detail_key_press)
        detail_view.connect(
            "button-press-event", self.on_detail_middle_press, row, item
        )
        detail_view.connect_after("button-press-event", self.on_task_edit_click)
        detail_view.connect(
            "motion-notify-event", self.on_detail_reorder_motion, row, item
        )
        detail_view.connect(
            "button-release-event", self.on_detail_reorder_release, row, item
        )
        detail_view.connect(
            "populate-popup", self.on_detail_populate_popup, row, item
        )
        row.detail_box.show_all()
        return item

    @staticmethod
    def get_buffer_text(text_buffer):
        start, end = text_buffer.get_bounds()
        return text_buffer.get_text(start, end, True)

    def register_undo_buffer(self, text_buffer):
        self._undo_histories[id(text_buffer)] = {
            "buffer": text_buffer,
            "states": [self.get_buffer_text(text_buffer)],
            "index": 0,
            "pending": None,
            "restoring": False,
        }
        text_buffer.connect("changed", self.on_undo_buffer_changed)

    def unregister_undo_buffer(self, text_buffer):
        history = self._undo_histories.pop(id(text_buffer), None)
        if history and history["pending"] is not None:
            GLib.source_remove(history["pending"])

    def on_undo_buffer_changed(self, text_buffer):
        history = self._undo_histories.get(id(text_buffer))
        if history is None or history["restoring"]:
            return
        if history["pending"] is not None:
            GLib.source_remove(history["pending"])
        history["pending"] = GLib.timeout_add(400, self.commit_undo_snapshot, text_buffer)

    def commit_undo_snapshot(self, text_buffer):
        history = self._undo_histories.get(id(text_buffer))
        if history is None:
            return False
        history["pending"] = None
        current = self.get_buffer_text(text_buffer)
        if current == history["states"][history["index"]]:
            return False
        del history["states"][history["index"] + 1 :]
        history["states"].append(current)
        if len(history["states"]) > 100:
            history["states"].pop(0)
        history["index"] = len(history["states"]) - 1
        return False

    def reset_undo_history(self, text_buffer):
        history = self._undo_histories.get(id(text_buffer))
        if history is None:
            return
        if history["pending"] is not None:
            GLib.source_remove(history["pending"])
        history["states"] = [self.get_buffer_text(text_buffer)]
        history["index"] = 0
        history["pending"] = None

    def restore_undo_state(self, text_buffer, text):
        history = self._undo_histories[id(text_buffer)]
        history["restoring"] = True
        text_buffer.set_text(text)
        text_buffer.place_cursor(text_buffer.get_end_iter())
        history["restoring"] = False

    def undo_buffer(self, text_buffer):
        self.commit_undo_snapshot(text_buffer)
        history = self._undo_histories.get(id(text_buffer))
        if history is None or history["index"] == 0:
            return
        history["index"] -= 1
        self.restore_undo_state(text_buffer, history["states"][history["index"]])

    def redo_buffer(self, text_buffer):
        self.commit_undo_snapshot(text_buffer)
        history = self._undo_histories.get(id(text_buffer))
        if history is None or history["index"] >= len(history["states"]) - 1:
            return
        history["index"] += 1
        self.restore_undo_state(text_buffer, history["states"][history["index"]])

    def handle_undo_shortcut(self, text_view, event):
        control = bool(event.state & Gdk.ModifierType.CONTROL_MASK)
        is_z = Gdk.keyval_to_lower(event.keyval) == Gdk.KEY_z
        if not (control and is_z):
            return False
        if event.state & Gdk.ModifierType.SHIFT_MASK:
            self.redo_buffer(text_view.get_buffer())
        else:
            self.undo_buffer(text_view.get_buffer())
        return True

    def handle_clipboard_shortcut(self, text_view, event):
        if not (event.state & Gdk.ModifierType.CONTROL_MASK):
            return False
        keyval = Gdk.keyval_to_lower(event.keyval)
        if keyval not in (Gdk.KEY_x, Gdk.KEY_c, Gdk.KEY_v):
            return False
        text_buffer = text_view.get_buffer()
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        if keyval == Gdk.KEY_x:
            text_buffer.cut_clipboard(clipboard, True)
        elif keyval == Gdk.KEY_c:
            text_buffer.copy_clipboard(clipboard)
        else:
            text_buffer.paste_clipboard(clipboard, None, True)
        return True

    def add_new_task(self):
        text = self.get_buffer_text(self.new_task_buffer).strip()
        if not text:
            return
        task_id = self.db.add(self.selected_date, text)
        self.append_task_row(task_id, text)
        self.new_task_buffer.set_text("")
        self.reset_undo_history(self.new_task_buffer)
        self.update_empty_state()
        self.task_list.show_all()
        self.refresh_calendar_marks()
        self.new_task_view.grab_focus()

    def on_composer_key_press(self, view, event):
        if self.handle_undo_shortcut(view, event):
            return True
        if self.handle_clipboard_shortcut(view, event):
            return True
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            if event.state & Gdk.ModifierType.SHIFT_MASK:
                return False
            self.add_new_task()
            return True
        return False

    def on_task_key_press(self, view, event):
        if self.handle_undo_shortcut(view, event):
            return True
        if self.handle_clipboard_shortcut(view, event):
            return True
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            if event.state & Gdk.ModifierType.SHIFT_MASK:
                return False
            self.new_task_view.grab_focus()
            return True
        return False

    def on_detail_key_press(self, view, event):
        if self.handle_undo_shortcut(view, event):
            return True
        if self.handle_clipboard_shortcut(view, event):
            return True
        return False

    def on_task_toggled(self, check, task_id, row):
        completed = check.get_active()
        self.db.update_completed(task_id, completed)
        row.completed = completed
        self.set_row_completed_style(row, completed)

    def set_row_completed_style(self, row, completed):
        context = row.get_style_context()
        if completed:
            context.add_class("done")
        else:
            context.remove_class("done")
        self.set_buffer_completed_style(row.task_view.get_buffer(), completed)
        for detail_item in row.detail_box.get_children():
            self.set_buffer_completed_style(
                detail_item.detail_view.get_buffer(), completed
            )

    @staticmethod
    def set_buffer_completed_style(text_buffer, completed):
        start, end = text_buffer.get_bounds()
        text_buffer.remove_tag_by_name("completed", start, end)
        if completed:
            text_buffer.apply_tag_by_name("completed", start, end)

    def on_task_text_changed(self, task_buffer, task_id, row):
        if not self._loading_rows:
            self.db.update_text(task_id, self.get_buffer_text(task_buffer))
            self.set_buffer_completed_style(task_buffer, row.completed)

    def on_detail_text_changed(self, detail_buffer, detail_id, row, _item):
        if not self._loading_rows:
            self.db.update_detail_text(
                detail_id, self.get_buffer_text(detail_buffer)
            )
            self.set_buffer_completed_style(detail_buffer, row.completed)

    @staticmethod
    def sort_task_rows(first, second, _user_data=None):
        return (first.sort_position > second.sort_position) - (
            first.sort_position < second.sort_position
        )

    def persist_current_order(self):
        rows = self.task_list.get_children()
        for position, row in enumerate(rows):
            row.sort_position = position
        self.db.update_positions([row.task_id for row in rows])

    def on_task_middle_press(self, task_view, event, row):
        if event.button != Gdk.BUTTON_MIDDLE:
            return False
        if self._detail_reorder_item is not None:
            self.finish_detail_reorder(self._detail_reorder_item)
        if self._reorder_row is not None:
            self.finish_task_reorder(self._reorder_row)
        self._reorder_row = row
        self._reorder_view = task_view
        row.get_style_context().add_class("reordering")
        task_view.grab_add()
        text_window = task_view.get_window(Gtk.TextWindowType.TEXT)
        if text_window is not None:
            display = task_view.get_display()
            cursor = Gdk.Cursor.new_from_name(display, "grabbing")
            if cursor is None:
                cursor = Gdk.Cursor.new_for_display(display, Gdk.CursorType.FLEUR)
            text_window.set_cursor(cursor)
        return True

    def row_nearest_to_pointer(self, pointer_y_root):
        nearest = None
        nearest_distance = None
        for candidate in self.task_list.get_children():
            text_window = candidate.task_view.get_window(Gtk.TextWindowType.TEXT)
            if text_window is None:
                continue
            _success, _origin_x, origin_y = text_window.get_origin()
            center_y = origin_y + candidate.get_allocated_height() / 2
            distance = abs(pointer_y_root - center_y)
            if nearest_distance is None or distance < nearest_distance:
                nearest = candidate
                nearest_distance = distance
        return nearest

    def on_task_reorder_motion(self, _task_view, event, row):
        if self._reorder_row is not row:
            return False
        target = self.row_nearest_to_pointer(event.y_root)
        if target is not None and target is not row:
            self.move_task_row(row, target.get_index())
        return True

    def move_task_row(self, row, target_index):
        rows = self.task_list.get_children()
        old_index = rows.index(row)
        if old_index == target_index:
            return
        rows.pop(old_index)
        rows.insert(target_index, row)
        for position, current_row in enumerate(rows):
            current_row.sort_position = position
        self.task_list.invalidate_sort()
        self.db.update_positions([current_row.task_id for current_row in rows])

    def on_task_reorder_release(self, _task_view, event, row):
        if event.button == Gdk.BUTTON_MIDDLE and self._reorder_row is row:
            self.finish_task_reorder(row)
            return True
        return False

    def finish_task_reorder(self, row):
        row.get_style_context().remove_class("reordering")
        if self._reorder_view is not None:
            text_window = self._reorder_view.get_window(Gtk.TextWindowType.TEXT)
            if text_window is not None:
                text_window.set_cursor(None)
            if self._reorder_view.has_grab():
                self._reorder_view.grab_remove()
        self._reorder_row = None
        self._reorder_view = None

    def on_detail_middle_press(self, detail_view, event, row, item):
        if event.button != Gdk.BUTTON_MIDDLE:
            return False
        if self._reorder_row is not None:
            self.finish_task_reorder(self._reorder_row)
        if self._detail_reorder_item is not None:
            self.finish_detail_reorder(self._detail_reorder_item)
        self._detail_reorder_item = item
        self._detail_reorder_view = detail_view
        self._detail_reorder_parent = row
        item.get_style_context().add_class("reordering")
        detail_view.grab_add()
        text_window = detail_view.get_window(Gtk.TextWindowType.TEXT)
        if text_window is not None:
            display = detail_view.get_display()
            cursor = Gdk.Cursor.new_from_name(display, "grabbing")
            if cursor is None:
                cursor = Gdk.Cursor.new_for_display(display, Gdk.CursorType.FLEUR)
            text_window.set_cursor(cursor)
        return True

    def detail_nearest_to_pointer(self, row, pointer_y_root):
        nearest = None
        nearest_distance = None
        for candidate in row.detail_box.get_children():
            text_window = candidate.detail_view.get_window(Gtk.TextWindowType.TEXT)
            if text_window is None:
                continue
            _success, _origin_x, origin_y = text_window.get_origin()
            center_y = origin_y + candidate.get_allocated_height() / 2
            distance = abs(pointer_y_root - center_y)
            if nearest_distance is None or distance < nearest_distance:
                nearest = candidate
                nearest_distance = distance
        return nearest

    def on_detail_reorder_motion(self, _detail_view, event, row, item):
        if self._detail_reorder_item is not item:
            return False
        target = self.detail_nearest_to_pointer(row, event.y_root)
        if target is not None and target is not item:
            self.move_detail_item(row, item, target)
        return True

    def move_detail_item(self, row, item, target):
        items = row.detail_box.get_children()
        old_index = items.index(item)
        target_index = items.index(target)
        if old_index == target_index:
            return
        row.detail_box.reorder_child(item, target_index)
        items = row.detail_box.get_children()
        for position, current_item in enumerate(items):
            current_item.sort_position = position
        self.db.update_detail_positions(
            [current_item.detail_id for current_item in items]
        )

    def on_detail_reorder_release(self, _detail_view, event, _row, item):
        if event.button == Gdk.BUTTON_MIDDLE and self._detail_reorder_item is item:
            self.finish_detail_reorder(item)
            return True
        return False

    def finish_detail_reorder(self, item):
        item.get_style_context().remove_class("reordering")
        if self._detail_reorder_view is not None:
            text_window = self._detail_reorder_view.get_window(
                Gtk.TextWindowType.TEXT
            )
            if text_window is not None:
                text_window.set_cursor(None)
            if self._detail_reorder_view.has_grab():
                self._detail_reorder_view.grab_remove()
        self._detail_reorder_item = None
        self._detail_reorder_view = None
        self._detail_reorder_parent = None

    def on_task_edit_click(self, task_view, event):
        if event.button != Gdk.BUTTON_PRIMARY:
            return False
        task_view.grab_focus()
        window_type = (
            task_view.get_window_type(event.window)
            if event.window is not None
            else Gtk.TextWindowType.WIDGET
        )
        buffer_x, buffer_y = task_view.window_to_buffer_coords(
            window_type, int(event.x), int(event.y)
        )
        _inside, text_iter = task_view.get_iter_at_location(buffer_x, buffer_y)
        text_buffer = task_view.get_buffer()
        text_buffer.place_cursor(text_iter)
        task_view.set_cursor_visible(True)
        task_view.scroll_mark_onscreen(text_buffer.get_insert())
        return True

    def on_task_populate_popup(self, _task_view, menu, task_id, row):
        for child in menu.get_children():
            menu.remove(child)
        detail_item = Gtk.MenuItem(label="내용 추가")
        detail_item.connect("activate", self.on_task_add_detail, task_id, row)
        menu.append(detail_item)
        carry_item = Gtk.MenuItem(label="내일로 이월")
        carry_item.connect("activate", self.on_task_carry_over, task_id, row)
        menu.append(carry_item)
        menu.append(Gtk.SeparatorMenuItem())
        delete_item = Gtk.MenuItem(label="삭제")
        delete_item.connect("activate", self.on_task_delete, task_id, row)
        menu.append(delete_item)
        menu.show_all()

    def on_detail_populate_popup(self, _detail_view, menu, row, item):
        for child in menu.get_children():
            menu.remove(child)
        add_item = Gtk.MenuItem(label="내용 추가")
        add_item.connect("activate", self.on_task_add_detail, row.task_id, row)
        menu.append(add_item)
        menu.append(Gtk.SeparatorMenuItem())
        delete_item = Gtk.MenuItem(label="내용 삭제")
        delete_item.connect("activate", self.on_detail_delete, row, item)
        menu.append(delete_item)
        menu.show_all()

    def on_task_add_detail(self, _menu_item, task_id, row):
        detail_id = self.db.add_detail(task_id)
        item = self.append_detail_row(row, detail_id)
        row.show_all()
        item.detail_view.grab_focus()
        detail_buffer = item.detail_view.get_buffer()
        detail_buffer.place_cursor(detail_buffer.get_end_iter())

    def on_task_carry_over(self, _menu_item, _task_id, row):
        text = self.get_buffer_text(row.task_view.get_buffer())
        next_date = self.selected_date + timedelta(days=1)
        new_task_id = self.db.add(next_date, text)
        for detail_item in row.detail_box.get_children():
            detail_text = self.get_buffer_text(
                detail_item.detail_view.get_buffer()
            )
            self.db.add_detail(new_task_id, detail_text)
        self.refresh_calendar_marks()

    def on_detail_delete(self, _menu_item, row, item):
        self.db.delete_detail(item.detail_id)
        self.unregister_undo_buffer(item.detail_view.get_buffer())
        row.detail_box.remove(item)
        self.persist_detail_order(row)

    def persist_detail_order(self, row):
        items = row.detail_box.get_children()
        for position, item in enumerate(items):
            item.sort_position = position
        self.db.update_detail_positions([item.detail_id for item in items])

    def on_task_delete(self, _menu_item, task_id, row):
        self.db.delete(task_id)
        self.unregister_undo_buffer(row.task_view.get_buffer())
        for detail_item in row.detail_box.get_children():
            self.unregister_undo_buffer(detail_item.detail_view.get_buffer())
        self.task_list.remove(row)
        self.persist_current_order()
        self.update_empty_state()
        self.refresh_calendar_marks()

    def update_empty_state(self):
        self.empty_label.set_visible(len(self.task_list.get_children()) == 0)

    def on_key_press(self, _window, event):
        if event.keyval == Gdk.KEY_Escape and self.stack.get_visible_child_name() == "checklist":
            self.show_calendar()
            return True
        if (
            event.state & Gdk.ModifierType.CONTROL_MASK
            and event.keyval in (Gdk.KEY_n, Gdk.KEY_N)
            and self.stack.get_visible_child_name() == "checklist"
        ):
            self.new_task_view.grab_focus()
            return True
        return False

    def on_delete_event(self, _window, _event):
        self.save_window_geometry()
        self._geometry_saved = True
        return False

    def save_window_geometry(self):
        x, y = self.get_position()
        width, height = self.get_size()
        self.db.set_window_geometry(x, y, width, height)

    def on_destroy(self, _window):
        if not self._geometry_saved:
            self.save_window_geometry()
        for history in self._undo_histories.values():
            if history["pending"] is not None:
                GLib.source_remove(history["pending"])
        self.db.close()


class DailyChecklistApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        window = self.props.active_window
        if window is None:
            window = DailyChecklistWindow(self)
        window.show_all()
        window.present()


if __name__ == "__main__":
    app = DailyChecklistApplication()
    raise SystemExit(app.run(None))
