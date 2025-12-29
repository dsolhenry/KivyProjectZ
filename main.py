"""
Phenry Todo Application
Author: Phenry Dsolemn
Version: 1.0
"""

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix import card
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
import json
import os
from datetime import datetime

class TodoItem(OneLineIconListItem):
    """Custom list item for todo tasks"""
    
    def __init__(self, text="", task_id=0, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.task_id = task_id
        
        # Add checkbox icon
        self.icon = IconLeftWidget(
            icon="checkbox-blank-outline",
            theme_text_color="Primary"
        )
        self.icon.bind(on_release=self.toggle_task)
        self.add_widget(self.icon)
        
    def toggle_task(self, instance):
        """Toggle task completion"""
        if self.icon.icon == "checkbox-blank-outline":
            self.icon.icon = "checkbox-marked"
            self.theme_text_color = "Hint"
        else:
            self.icon.icon = "checkbox-blank-outline"
            self.theme_text_color = "Primary"
        
        # Save state to app
        app = MDApp.get_running_app()
        app.toggle_task_completion(self.task_id)
    
    def on_touch_down(self, touch):
        """Handle long press for delete"""
        if self.collide_point(*touch.pos):
            Clock.schedule_once(lambda dt: self.show_delete_dialog(touch), 0.5)
        return super().on_touch_down(touch)
    
    def show_delete_dialog(self, touch):
        """Show delete confirmation dialog"""
        if self.collide_point(*touch.pos):
            app = MDApp.get_running_app()
            app.show_delete_dialog(self.task_id, self.text)

class TodoScreen(MDScreen):
    """Main screen for the todo app"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "todo_screen"
        
        # Main layout
        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing=10,
            padding=20
        )
        
        # App Bar
        app_bar = MDTopAppBar(
            title="Phenry Todo List",
            elevation=4,
            md_bg_color="#4CAF50",
            specific_text_color="#FFFFFF"
        )
        
        # Add menu button
        app_bar.right_action_items = [
            ["delete-sweep", lambda x: self.clear_completed()],
            ["information", lambda x: self.show_info()]
        ]
        
        # Add stats label
        self.stats_label = MDLabel(
            text="0 tasks | 0 completed",
            halign="center",
            theme_text_color="Secondary",
            font_style="Caption"
        )
        
        # Task input area
        input_card = card(
            size_hint_y=None,
            height=80,
            elevation=2,
            padding=15,
            radius=15
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
        
        # Task list area
        scroll = ScrollView()
        self.task_list = MDList(
            spacing=10,
            padding=10
        )
        scroll.add_widget(self.task_list)
        
        # Add all widgets to screen
        main_layout.add_widget(app_bar)
        main_layout.add_widget(self.stats_label)
        main_layout.add_widget(input_card)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def add_task_from_input(self, *args):
        """Add task from text input"""
        task_text = self.task_input.text.strip()
        if task_text:
            app = MDApp.get_running_app()
            app.add_task(task_text)
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

class TodoApp(MDApp):
    """Main application class"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tasks = []
        self.next_id = 1
        self.data_file = "todo_data.json"
        self.dialog = None
        
        # Load saved tasks
        self.load_tasks()
    
    def build(self):
        """Build the application"""
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"
        self.title = "Todo App"
        
        # Create screen manager
        self.screen_manager = MDScreenManager()
        
        # Add todo screen
        todo_screen = TodoScreen()
        self.screen_manager.add_widget(todo_screen)
        
        return self.screen_manager
    
    def on_start(self):
        """Called when app starts"""
        self.update_display()
    
    def add_task(self, text):
        """Add a new task"""
        if text:
            task = {
                "id": self.next_id,
                "text": text,
                "completed": False,
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
    
    def clear_completed_tasks(self):
        """Clear all completed tasks"""
        self.tasks = [task for task in self.tasks if not task["completed"]]
        self.save_tasks()
        self.update_display()
    
    def update_display(self):
        """Update the task list display"""
        screen = self.screen_manager.get_screen("todo_screen")
        screen.task_list.clear_widgets()
        
        # Add tasks to list
        for task in self.tasks:
            item = TodoItem(
                text=task["text"],
                task_id=task["id"]
            )
            
            # Set initial state
            if task["completed"]:
                item.icon.icon = "checkbox-marked"
                item.theme_text_color = "Hint"
            
            screen.task_list.add_widget(item)
        
        # Update stats
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t["completed"]])
        screen.stats_label.text = f"{total} tasks | {completed} completed"
    
    def show_delete_dialog(self, task_id, task_text):
        """Show delete confirmation dialog"""
        if not self.dialog:
            self.dialog = MDDialog(
                title="Delete Task?",
                text=f"Delete '{task_text[:30]}...'?",
                buttons=[
                    MDRaisedButton(
                        text="CANCEL",
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="DELETE",
                        md_bg_color="#F44336",
                        on_release=lambda x: self.confirm_delete(task_id)
                    )
                ]
            )
        self.dialog.open()
    
    def confirm_delete(self, task_id):
        """Confirm and delete task"""
        self.delete_task(task_id)
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
    
    def show_info_dialog(self):
        """Show information about the app"""
        info_text = """
        Todo App v1.0
        
        Features:
        • Add new tasks
        • Mark tasks as complete
        • Delete individual tasks
        • Clear all completed tasks
        • Data persistence
        
        Long press on any task to delete it.
        
        Built with KivyMD
        """
        
        info_dialog = MDDialog(
            title="About Todo App",
            text=info_text,
            buttons=[
                MDRaisedButton(
                    text="OK",
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
                    "next_id": self.next_id
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
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.tasks = []
            self.next_id = 1
    
    def on_stop(self):
        """Called when app stops"""
        self.save_tasks()

if __name__ == '__main__':
    TodoApp().run()