#!/usr/bin/env python3
import os
import sqlite3
from datetime import date, timedelta

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gio, GLib, Gtk


APP_ID = "io.github.kimyina.checklist"
WEEKDAYS_KO = ("월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일")


CSS = b"""
* {
  font-family: Pretendard, sans-serif;
  font-size: 10pt;
}
window {
  background: #ffffff;
  color: #242424;
}
.topbar {
  background: #ffffff;
  border-bottom: 1px solid #d9d9d9;
  padding: 5px 7px;
}
.app-title, .date-title {
  font-weight: 600;
}
.calendar-wrap {
  padding: 0 10px;
}
.calendar-shell {
  background: #ffffff;
  border: 1px solid #d7d7d7;
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
  background-color: rgba(70, 70, 70, 0.07);
}
.calendar-weekdays {
  padding: 1px 4px 0 4px;
}
.calendar-weekday {
  color: #a5a5a5;
}
.calendar-grid {
  padding: 0 4px 3px 4px;
}
.calendar-day,
.calendar-day:focus {
  color: #333333;
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
  background-color: rgba(70, 70, 70, 0.07);
}
.calendar-day.today {
  color: #202020;
  background-color: rgba(55, 55, 55, 0.18);
  border: 1px solid rgba(45, 45, 45, 0.42);
  font-weight: 700;
}
.calendar-day.has-tasks {
  font-weight: 700;
  box-shadow: inset 0 -2px rgba(55, 55, 55, 0.42);
}
.calendar-day.other-month {
  color: rgba(70, 70, 70, 0.20);
}
.task-list,
.task-list:focus {
  background: #ffffff;
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
  color: #242424;
  background: transparent;
  padding: 3px 5px 3px 7px;
  border: 0;
  outline-color: transparent;
  box-shadow: none;
}
.task-row.reordering {
  color: #242424;
  background-color: #ffffff;
  border: 1px solid rgba(40, 40, 40, 0.13);
  border-radius: 7px;
  margin: 3px 6px;
  padding: 2px 6px;
  box-shadow: 0 7px 16px rgba(0, 0, 0, 0.24);
}
.task-row.reordering .task-text,
.task-row.reordering .task-text text,
.task-row.reordering .task-text text:focus {
  background-color: #ffffff;
}
.task-text,
.task-text:focus {
  background: transparent;
  border: 0;
  padding: 6px 3px;
  outline-color: transparent;
  box-shadow: none;
}
.task-text text {
  color: #242424;
  background: transparent;
}
.task-text text:focus {
  color: #242424;
  background-color: rgba(70, 70, 70, 0.055);
  border-color: transparent;
  outline-color: transparent;
  box-shadow: none;
}
.task-text text:selected,
.task-text text:focus:selected,
.task-list selection {
  color: #242424;
  background-color: rgba(70, 70, 70, 0.10);
  outline-color: transparent;
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
  background: #ffffff;
  padding: 5px 8px 7px 31px;
  border-top: 1px solid #eeeeee;
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
  background: transparent;
}
.composer text:selected,
.composer text:focus:selected {
  color: #242424;
  background-color: rgba(70, 70, 70, 0.10);
}
.composer-hint {
  color: #999999;
}
.empty-label {
  color: #888888;
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

    def close(self):
        self.connection.close()


class DailyChecklistWindow(Gtk.ApplicationWindow):
    def __init__(self, application):
        super().__init__(application=application, title="checklist")
        self.set_default_size(310, 280)
        self.set_size_request(310, 280)
        self.set_resizable(False)
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            self.set_icon_from_file(icon_path)
        self.db = ChecklistDatabase()
        saved_position = self.db.get_window_position()
        self._position_saved = False
        if saved_position is None:
            self.set_position(Gtk.WindowPosition.CENTER)
        else:
            self.move(*saved_position)
        self.selected_date = date.today()
        self._loading_rows = False
        self._undo_histories = {}
        self._reorder_row = None
        self._reorder_view = None

        self.connect("delete-event", self.on_delete_event)
        self.connect("destroy", self.on_destroy)
        self.connect("key-press-event", self.on_key_press)

        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        Gtk.Settings.get_default().set_property("gtk-cursor-blink", False)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(160)
        self.add(self.stack)

        self.calendar_page = self.build_calendar_page()
        self.checklist_page = self.build_checklist_page()
        self.stack.add_named(self.calendar_page, "calendar")
        self.stack.add_named(self.checklist_page, "checklist")
        self.stack.set_visible_child_name("calendar")

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
            task_view = child.get_child().get_children()[1]
            self.unregister_undo_buffer(task_view.get_buffer())
            self.task_list.remove(child)
        for task_id, text, completed in self.db.tasks_for(self.selected_date):
            self.append_task_row(task_id, text, bool(completed))
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
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)

        check = Gtk.CheckButton()
        check.set_active(completed)
        check.set_tooltip_text("완료")
        box.pack_start(check, False, False, 0)

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
        task_buffer.create_tag("completed", strikethrough=True, foreground="#999999")
        self.register_undo_buffer(task_buffer)
        box.pack_start(task_view, True, True, 0)

        row.add(box)
        self.task_list.add(row)
        row.completed = completed
        self.set_row_completed_style(row, completed, task_buffer)

        check.connect("toggled", self.on_task_toggled, task_id, row, task_buffer)
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

    def on_task_toggled(self, check, task_id, row, task_buffer):
        completed = check.get_active()
        self.db.update_completed(task_id, completed)
        row.completed = completed
        self.set_row_completed_style(row, completed, task_buffer)

    def set_row_completed_style(self, row, completed, task_buffer):
        context = row.get_style_context()
        if completed:
            context.add_class("done")
        else:
            context.remove_class("done")
        start, end = task_buffer.get_bounds()
        task_buffer.remove_tag_by_name("completed", start, end)
        if completed:
            task_buffer.apply_tag_by_name("completed", start, end)

    def on_task_text_changed(self, task_buffer, task_id, row):
        if not self._loading_rows:
            self.db.update_text(task_id, self.get_buffer_text(task_buffer))
            self.set_row_completed_style(row, row.completed, task_buffer)

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
            task_view = candidate.get_child().get_children()[1]
            text_window = task_view.get_window(Gtk.TextWindowType.TEXT)
            if text_window is None:
                continue
            _success, _origin_x, origin_y = text_window.get_origin()
            center_y = origin_y + task_view.get_allocated_height() / 2
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
        carry_item = Gtk.MenuItem(label="내일로 이월")
        carry_item.connect("activate", self.on_task_carry_over, task_id, row)
        menu.append(carry_item)
        menu.append(Gtk.SeparatorMenuItem())
        delete_item = Gtk.MenuItem(label="삭제")
        delete_item.connect("activate", self.on_task_delete, task_id, row)
        menu.append(delete_item)
        menu.show_all()

    def on_task_carry_over(self, _menu_item, task_id, row):
        task_view = row.get_child().get_children()[1]
        text = self.get_buffer_text(task_view.get_buffer())
        next_date = self.selected_date + timedelta(days=1)
        self.db.add(next_date, text)
        self.refresh_calendar_marks()

    def on_task_delete(self, _menu_item, task_id, row):
        self.db.delete(task_id)
        task_view = row.get_child().get_children()[1]
        self.unregister_undo_buffer(task_view.get_buffer())
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
        self.db.set_window_position(*self.get_position())
        self._position_saved = True
        return False

    def on_destroy(self, _window):
        if not self._position_saved:
            self.db.set_window_position(*self.get_position())
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
