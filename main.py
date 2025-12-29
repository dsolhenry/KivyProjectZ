"""
Phenry Todo Application - Enhanced
Author: Phenry Dsolemn
Version: 2.0
"""

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList, ThreeLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.metrics import dp
import json
import os
from datetime import datetime

class TodoItem(ThreeLineAvatarIconListItem):
    """Custom list item for todo tasks"""
    
    def __init__(self, text="", task_id=0, completed=False, category="General", created_at="", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.secondary_text = f"Category: {category}"
        self.tertiary_text = f"Created: {created_at}"
        self.task_id = task_id
        self.category = category
        self.created_at = created_at
        self.completed = completed
        
        # Add checkbox icon
        self.checkbox = IconLeftWidget(
            icon="checkbox-blank-outline" if not completed else "checkbox-marked",
            theme_text_color="Primary" if not completed else "Hint"
        )
        self.checkbox.bind(on_release=self.toggle_task)
        self.add_widget(self.checkbox)
        
        # Add delete button
        self.delete_btn = IconRightWidget(
            icon="delete",
            theme_text_color="Error"
        )
        self.delete_btn.bind(on_release=self.delete_task)
        self.add_widget(self.delete_btn)
        
        # Set initial appearance
        if completed:
            self.theme_text_color = "Hint"
    
    def toggle_task(self, instance):
        """Toggle task completion"""
        if self.checkbox.icon == "checkbox-blank-outline":
            self.checkbox.icon = "checkbox-marked"
            self.checkbox.theme_text_color = "Hint"
            self.theme_text_color = "Hint"
        else:
            self.checkbox.icon = "checkbox-blank-outline"
            self.checkbox.theme_text_color = "Primary"
            self.theme_text_color = "Primary"
        
        app = MDApp.get_running_app()
        app.toggle_task_completion(self.task_id)
    
    def delete_task(self, instance):
        """Delete task with confirmation"""
        app = MDApp.get_running_app()
        app.show_delete_dialog(self.task_id, self.text)
    
    def on_release(self):
        """Edit task on tap"""
        app = MDApp.get_running_app()
        app.show_edit_dialog(self.task_id, self.text, self.category)

class TodoScreen(MDScreen):
    """Main screen for the todo app"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "todo_screen"
        
        # Main layout
        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing=10,
            padding=10
        )
        
        # App Bar
        self.app_bar = MDTopAppBar(
            title="Phenry Todo List",
            elevation=4,
            md_bg_color="#4CAF50",
            specific_text_color="#FFFFFF"
        )
        
        # Add menu buttons
        self.app_bar.right_action_items = [
            ["filter-variant", lambda x: self.show_filter_menu()],
            ["delete-sweep", lambda x: self.clear_completed()],
            ["information", lambda x: self.show_info()]
        ]
        
        # Filter chips area
        filter_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=10,
            padding=[10, 5]
        )
        
        self.filter_label = MDLabel(
            text="Filter: All Tasks",
            theme_text_color="Secondary",
            font_style="Caption",
            size_hint_x=0.4
        )
        
        filter_layout.add_widget(self.filter_label)
        
        # Add stats label
        self.stats_label = MDLabel(
            text="0 tasks | 0 completed",
            halign="right",
            theme_text_color="Secondary",
            font_style="Caption",
            size_hint_x=0.6
        )
        
        filter_layout.add_widget(self.stats_label)
        
        # Category selection
        category_card = MDCard(
            size_hint_y=None,
            height=dp(60),
            elevation=2,
            padding=10,
            radius=[15, 15, 0, 0]
        )
        
        category_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=10
        )
        
        category_label = MDLabel(
            text="Category:",
            size_hint_x=0.25,
            theme_text_color="Primary"
        )
        
        self.category_button = MDRaisedButton(
            text="General",
            size_hint_x=0.75,
            md_bg_color="#2196F3",
            on_release=lambda x: self.show_category_menu()
        )
        
        category_layout.add_widget(category_label)
        category_layout.add_widget(self.category_button)
        category_card.add_widget(category_layout)
        
        # Task input area
        input_card = MDCard(
            size_hint_y=None,
            height=dp(80),
            elevation=2,
            padding=15,
            radius=[0, 0, 15, 15]
        )
        
        input_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=15
        )
        
        self.task_input = MDTextField(
            hint_text="Add a new task...",
            mode="rectangle",
            size_hint_x=0.7,
            on_text_validate=self.add_task_from_input
        )
        
        add_button = MDRaisedButton(
            text="ADD",
            size_hint_x=0.3,
            md_bg_color="#4CAF50",
            on_release=lambda x: self.add_task_from_input()
        )
        
        input_layout.add_widget(self.task_input)
        input_layout.add_widget(add_button)
        input_card.add_widget(input_layout)
        
        # Search field
        self.search_field = MDTextField(
            hint_text="Search tasks...",
            mode="rectangle",
            size_hint_y=None,
            height=dp(50),
            icon_right="magnify",
            padding=[10, 0]
        )
        self.search_field.bind(text=self.on_search_text)
        
        # Task list area
        scroll = ScrollView()
        self.task_list = MDList(
            spacing=5,
            padding=5
        )
        scroll.add_widget(self.task_list)
        
        # Add all widgets to screen
        main_layout.add_widget(self.app_bar)
        main_layout.add_widget(filter_layout)
        main_layout.add_widget(category_card)
        main_layout.add_widget(input_card)
        main_layout.add_widget(self.search_field)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
        
        # Current filter
        self.current_filter = "all"
        self.current_category_filter = "All"
        self.search_text = ""
    
    def add_task_from_input(self, *args):
        """Add task from text input"""
        task_text = self.task_input.text.strip()
        if task_text:
            app = MDApp.get_running_app()
            category = self.category_button.text
            app.add_task(task_text, category)
            self.task_input.text = ""
            self.task_input.focus = True
    
    def clear_completed(self):
        """Clear all completed tasks"""
        app = MDApp.get_running_app()
        app.clear_completed_tasks()
    
    def show_info(self):
        """Show app information"""
        app = MDApp.get_running_app()
        app.show_info_dialog()
    
    def show_category_menu(self):
        """Show category selection menu"""
        app = MDApp.get_running_app()
        menu_items = []
        
        for category in app.categories:
            menu_items.append({
                "text": category,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=category: self.select_category(x)
            })
        
        self.category_menu = MDDropdownMenu(
            caller=self.category_button,
            items=menu_items,
            width_mult=4
        )
        self.category_menu.open()
    
    def select_category(self, category):
        """Select a category"""
        self.category_button.text = category
        self.category_menu.dismiss()
    
    def show_filter_menu(self):
        """Show filter menu"""
        app = MDApp.get_running_app()
        menu_items = [
            {
                "text": "All Tasks",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.set_filter("all")
            },
            {
                "text": "Active Tasks",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.set_filter("active")
            },
            {
                "text": "Completed Tasks",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.set_filter("completed")
            }
        ]
        
        # Add category filters
        for category in app.categories:
            menu_items.append({
                "text": f"Category: {category}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=category: self.set_category_filter(x)
            })
        
        self.filter_menu = MDDropdownMenu(
            caller=self.app_bar,
            items=menu_items,
            width_mult=4
        )
        self.filter_menu.open()
    
    def set_filter(self, filter_type):
        """Set task filter"""
        self.current_filter = filter_type
        self.current_category_filter = "All"
        
        filter_names = {
            "all": "All Tasks",
            "active": "Active Tasks",
            "completed": "Completed Tasks"
        }
        self.filter_label.text = f"Filter: {filter_names[filter_type]}"
        
        app = MDApp.get_running_app()
        app.update_display()
        self.filter_menu.dismiss()
    
    def set_category_filter(self, category):
        """Set category filter"""
        self.current_category_filter = category
        self.current_filter = "all"
        self.filter_label.text = f"Filter: {category}"
        
        app = MDApp.get_running_app()
        app.update_display()
        self.filter_menu.dismiss()
    
    def on_search_text(self, instance, value):
        """Handle search text change"""
        self.search_text = value.lower()
        app = MDApp.get_running_app()
        app.update_display()

class TodoApp(MDApp):
    """Main application class"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tasks = []
        self.next_id = 1
        self.data_file = "todo_data.json"
        self.categories = ["General", "Work", "Personal", "Shopping", "Health", "Study"]
        
        # Load saved tasks
        self.load_tasks()
    
    def build(self):
        """Build the application"""
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"
        self.title = "Phenry Todo App"
        
        # Create screen manager
        self.screen_manager = MDScreenManager()
        
        # Add todo screen
        self.todo_screen = TodoScreen()
        self.screen_manager.add_widget(self.todo_screen)
        
        return self.screen_manager
    
    def on_start(self):
        """Called when app starts"""
        self.update_display()
    
    def add_task(self, text, category="General"):
        """Add a new task"""
        if text:
            task = {
                "id": self.next_id,
                "text": text,
                "completed": False,
                "category": category,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            self.tasks.append(task)
            self.next_id += 1
            self.save_tasks()
            self.update_display()
    
    def toggle_task_completion(self, task_id):
        """Toggle task completion status"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = not task["completed"]
                break
        self.save_tasks()
        self.update_display()
    
    def delete_task(self, task_id):
        """Delete a task"""
        self.tasks = [task for task in self.tasks if task["id"] != task_id]
        self.save_tasks()
        self.update_display()
    
    def edit_task(self, task_id, new_text, new_category):
        """Edit an existing task"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["text"] = new_text
                task["category"] = new_category
                break
        self.save_tasks()
        self.update_display()
    
    def clear_completed_tasks(self):
        """Clear all completed tasks"""
        self.tasks = [task for task in self.tasks if not task["completed"]]
        self.save_tasks()
        self.update_display()
    
    def update_display(self):
        """Update the task list display"""
        screen = self.todo_screen
        screen.task_list.clear_widgets()
        
        # Filter tasks
        filtered_tasks = self.get_filtered_tasks()
        
        # Add tasks to list
        for task in filtered_tasks:
            item = TodoItem(
                text=task["text"],
                task_id=task["id"],
                completed=task["completed"],
                category=task.get("category", "General"),
                created_at=task.get("created_at", "")
            )
            
            screen.task_list.add_widget(item)
        
        # Update stats
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t["completed"]])
        active = total - completed
        screen.stats_label.text = f"{total} tasks | {active} active | {completed} done"
    
    def get_filtered_tasks(self):
        """Get filtered tasks based on current filter"""
        screen = self.todo_screen
        filtered = self.tasks
        
        # Apply completion filter
        if screen.current_filter == "active":
            filtered = [t for t in filtered if not t["completed"]]
        elif screen.current_filter == "completed":
            filtered = [t for t in filtered if t["completed"]]
        
        # Apply category filter
        if screen.current_category_filter != "All":
            filtered = [t for t in filtered if t.get("category", "General") == screen.current_category_filter]
        
        # Apply search filter
        if screen.search_text:
            filtered = [t for t in filtered if screen.search_text in t["text"].lower()]
        
        return filtered
    
    def show_delete_dialog(self, task_id, task_text):
        """Show delete confirmation dialog"""
        dialog = MDDialog(
            title="Delete Task?",
            text=f"Delete '{task_text[:50]}...'?" if len(task_text) > 50 else f"Delete '{task_text}'?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="DELETE",
                    md_bg_color="#F44336",
                    on_release=lambda x: self.confirm_delete(task_id, dialog)
                )
            ]
        )
        dialog.open()
    
    def confirm_delete(self, task_id, dialog):
        """Confirm and delete task"""
        self.delete_task(task_id)
        dialog.dismiss()
    
    def show_edit_dialog(self, task_id, current_text, current_category):
        """Show edit task dialog"""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=20,
            padding=20,
            size_hint_y=None,
            height=dp(200)
        )
        
        text_field = MDTextField(
            text=current_text,
            hint_text="Task text",
            mode="rectangle"
        )
        
        category_button = MDRaisedButton(
            text=current_category,
            size_hint_x=1,
            md_bg_color="#2196F3"
        )
        
        def show_cat_menu():
            menu_items = []
            for cat in self.categories:
                menu_items.append({
                    "text": cat,
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=cat: select_cat(x)
                })
            
            cat_menu = MDDropdownMenu(
                caller=category_button,
                items=menu_items,
                width_mult=4
            )
            cat_menu.open()
        
        def select_cat(cat):
            category_button.text = cat
        
        category_button.bind(on_release=lambda x: show_cat_menu())
        
        content.add_widget(text_field)
        content.add_widget(category_button)
        
        dialog = MDDialog(
            title="Edit Task",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="SAVE",
                    md_bg_color="#4CAF50",
                    on_release=lambda x: self.confirm_edit(task_id, text_field.text, category_button.text, dialog)
                )
            ]
        )
        dialog.open()
    
    def confirm_edit(self, task_id, new_text, new_category, dialog):
        """Confirm and edit task"""
        if new_text.strip():
            self.edit_task(task_id, new_text.strip(), new_category)
        dialog.dismiss()
    
    def show_info_dialog(self):
        """Show information about the app"""
        info_text = """Todo App v2.0 - Enhanced

Features:
• Add, edit, and delete tasks
• Mark tasks as complete
• Categorize tasks
• Filter by status or category
• Search tasks
• Clear completed tasks
• Persistent data storage

Tap any task to edit it.
Use the filter menu for quick views.

Built with KivyMD by Phenry Dsolemn"""
        
        info_dialog = MDDialog(
            title="About Todo App",
            text=info_text,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    md_bg_color="#4CAF50",
                    on_release=lambda x: info_dialog.dismiss()
                )
            ]
        )
        info_dialog.open()
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump({
                    "tasks": self.tasks,
                    "next_id": self.next_id,
                    "categories": self.categories
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def load_tasks(self):
        """Load tasks from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = data.get("tasks", [])
                    self.next_id = data.get("next_id", 1)
                    saved_categories = data.get("categories", [])
                    if saved_categories:
                        self.categories = saved_categories
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.tasks = []
            self.next_id = 1
    
    def on_stop(self):
        """Called when app stops"""
        self.save_tasks()

if __name__ == '__main__':
    TodoApp().run()