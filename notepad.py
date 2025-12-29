from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty, ListProperty
import json
import os
from datetime import datetime

Window.size = (400, 700)

KV = '''
#:import utils kivy.utils

<NoteCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: "180dp"
    padding: "12dp"
    spacing: "8dp"
    elevation: 2
    radius: [12, 12, 12, 12]
    md_bg_color: self.card_color
    ripple_behavior: True
    
    MDBoxLayout:
        size_hint_y: None
        height: "32dp"
        spacing: "8dp"
        
        MDLabel:
            text: root.note_title
            font_style: "H6"
            bold: True
            size_hint_x: 0.85
            theme_text_color: "Custom"
            text_color: 0, 0, 0, 0.87
        
        MDIconButton:
            icon: "dots-vertical"
            size_hint_x: 0.15
            on_release: root.show_menu(self)
    
    MDLabel:
        text: root.note_content
        size_hint_y: 1
        theme_text_color: "Custom"
        text_color: 0, 0, 0, 0.6
        font_size: "14sp"
        text_size: self.width, None
        shorten: True
        shorten_from: "right"
        max_lines: 4
    
    MDLabel:
        text: root.note_date
        size_hint_y: None
        height: "20dp"
        font_size: "12sp"
        theme_text_color: "Custom"
        text_color: 0, 0, 0, 0.4

MDScreenManager:
    NotesListScreen:
    NoteEditorScreen:

<NotesListScreen>:
    name: 'notes_list'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Notebook"
            md_bg_color: app.theme_cls.primary_color
            elevation: 3
            right_action_items: [["magnify", lambda x: app.show_search()], ["view-grid", lambda x: app.toggle_view()]]
        
        MDBoxLayout:
            orientation: 'vertical'
            padding: "8dp"
            
            MDScrollView:
                id: scroll_view
                MDGridLayout:
                    id: notes_grid
                    cols: 2
                    spacing: "12dp"
                    padding: "8dp"
                    adaptive_height: True
        
        MDFloatingActionButton:
            icon: "plus"
            md_bg_color: app.theme_cls.primary_color
            pos_hint: {"center_x": 0.85, "center_y": 0.08}
            on_release: app.new_note()

<NoteEditorScreen>:
    name: 'note_editor'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Note"
            md_bg_color: app.theme_cls.primary_color
            elevation: 3
            left_action_items: [["arrow-left", lambda x: app.back_to_list()]]
            right_action_items: [["check", lambda x: app.save_note()]]
        
        MDScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                padding: "16dp"
                spacing: "16dp"
                adaptive_height: True
                
                MDTextField:
                    id: title_field
                    hint_text: "Title"
                    mode: "fill"
                    size_hint_y: None
                    height: "56dp"
                    font_size: "20sp"
                
                MDTextField:
                    id: content_field
                    hint_text: "Take a note..."
                    mode: "fill"
                    multiline: True
                    size_hint_y: None
                    height: "400dp"
                
                MDBoxLayout:
                    size_hint_y: None
                    height: "48dp"
                    spacing: "12dp"
                    padding: "0dp"
                    
                    MDLabel:
                        text: "Color:"
                        size_hint_x: 0.2
                        halign: "left"
                    
                    MDIconButton:
                        icon: "circle"
                        theme_text_color: "Custom"
                        text_color: utils.get_color_from_hex("#FFFFFF")
                        md_bg_color: utils.get_color_from_hex("#FFFFFF")
                        on_release: app.set_note_color("#FFFFFF")
                    
                    MDIconButton:
                        icon: "circle"
                        theme_text_color: "Custom"
                        text_color: utils.get_color_from_hex("#FFE0B2")
                        md_bg_color: utils.get_color_from_hex("#FFE0B2")
                        on_release: app.set_note_color("#FFE0B2")
                    
                    MDIconButton:
                        icon: "circle"
                        theme_text_color: "Custom"
                        text_color: utils.get_color_from_hex("#FFCCBC")
                        md_bg_color: utils.get_color_from_hex("#FFCCBC")
                        on_release: app.set_note_color("#FFCCBC")
                    
                    MDIconButton:
                        icon: "circle"
                        theme_text_color: "Custom"
                        text_color: utils.get_color_from_hex("#B2DFDB")
                        md_bg_color: utils.get_color_from_hex("#B2DFDB")
                        on_release: app.set_note_color("#B2DFDB")
                    
                    MDIconButton:
                        icon: "circle"
                        theme_text_color: "Custom"
                        text_color: utils.get_color_from_hex("#C5CAE9")
                        md_bg_color: utils.get_color_from_hex("#C5CAE9")
                        on_release: app.set_note_color("#C5CAE9")
                    
                    MDIconButton:
                        icon: "circle"
                        theme_text_color: "Custom"
                        text_color: utils.get_color_from_hex("#F8BBD0")
                        md_bg_color: utils.get_color_from_hex("#F8BBD0")
                        on_release: app.set_note_color("#F8BBD0")
'''


class NoteCard(MDCard, ButtonBehavior):
    note_title = StringProperty("")
    note_content = StringProperty("")
    note_date = StringProperty("")
    card_color = ListProperty([1, 1, 1, 1])
    
    def __init__(self, note_data, index, app_instance, **kwargs):
        self.note_data = note_data
        self.index = index
        self.app_instance = app_instance
        self.note_title = note_data.get('title', 'Untitled')
        self.note_content = note_data.get('content', 'No content')
        self.note_date = note_data.get('date', '')
        
        # Convert hex color to RGBA
        color_hex = note_data.get('color', '#FFFFFF')
        from kivy.utils import get_color_from_hex
        self.card_color = get_color_from_hex(color_hex)
        
        super().__init__(**kwargs)
        self.menu = None
    
    def on_release(self):
        self.app_instance.open_note(self.index)
    
    def show_menu(self, button):
        menu_items = [
            {
                "text": "Delete",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.delete_note(),
            }
        ]
        self.menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=3,
        )
        self.menu.open()
    
    def delete_note(self):
        if self.menu:
            self.menu.dismiss()
        self.app_instance.delete_note_by_index(self.index)


class NotesListScreen(MDScreen):
    pass


class NoteEditorScreen(MDScreen):
    pass


class NotepadApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notes = []
        self.current_note_index = None
        self.current_note_color = "#FFFFFF"
        self.notes_file = 'notes.json'
        self.grid_view = True
        
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "600"
        return Builder.load_string(KV)
    
    def on_start(self):
        self.load_notes()
        self.refresh_notes_list()
    
    def load_notes(self):
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, 'r') as f:
                    self.notes = json.load(f)
            except:
                self.notes = []
        else:
            self.notes = []
    
    def save_notes_to_file(self):
        with open(self.notes_file, 'w') as f:
            json.dump(self.notes, f, indent=2)
    
    def refresh_notes_list(self):
        list_screen = self.root.get_screen('notes_list')
        notes_grid = list_screen.ids.notes_grid
        notes_grid.clear_widgets()
        
        for idx, note in enumerate(reversed(self.notes)):
            real_idx = len(self.notes) - 1 - idx
            card = NoteCard(note, real_idx, self)
            notes_grid.add_widget(card)
    
    def toggle_view(self):
        list_screen = self.root.get_screen('notes_list')
        notes_grid = list_screen.ids.notes_grid
        self.grid_view = not self.grid_view
        notes_grid.cols = 2 if self.grid_view else 1
        self.refresh_notes_list()
    
    def show_search(self):
        # Placeholder for search functionality
        self.show_dialog("Search", "Search feature coming soon!")
    
    def new_note(self):
        self.current_note_index = None
        self.current_note_color = "#FFFFFF"
        editor_screen = self.root.get_screen('note_editor')
        editor_screen.ids.title_field.text = ''
        editor_screen.ids.content_field.text = ''
        self.root.current = 'note_editor'
    
    def open_note(self, index):
        self.current_note_index = index
        note = self.notes[index]
        self.current_note_color = note.get('color', '#FFFFFF')
        editor_screen = self.root.get_screen('note_editor')
        editor_screen.ids.title_field.text = note.get('title', '')
        editor_screen.ids.content_field.text = note.get('content', '')
        self.root.current = 'note_editor'
    
    def set_note_color(self, color):
        self.current_note_color = color
    
    def save_note(self):
        editor_screen = self.root.get_screen('note_editor')
        title = editor_screen.ids.title_field.text
        content = editor_screen.ids.content_field.text
        
        if not title and not content:
            self.show_dialog("Error", "Cannot save empty note")
            return
        
        current_date = datetime.now().strftime("%b %d, %Y")
        
        note = {
            'title': title if title else 'Untitled',
            'content': content,
            'color': self.current_note_color,
            'date': current_date
        }
        
        if self.current_note_index is None:
            self.notes.append(note)
        else:
            # Keep the original date if updating
            if 'date' in self.notes[self.current_note_index]:
                note['date'] = self.notes[self.current_note_index]['date']
            self.notes[self.current_note_index] = note
        
        self.save_notes_to_file()
        self.refresh_notes_list()
        self.back_to_list()
    
    def delete_note_by_index(self, index):
        dialog = MDDialog(
            title="Delete Note",
            text="Are you sure you want to delete this note?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="DELETE",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.error_color,
                    on_release=lambda x: self.confirm_delete_by_index(dialog, index)
                ),
            ],
        )
        dialog.open()
    
    def confirm_delete_by_index(self, dialog, index):
        del self.notes[index]
        self.save_notes_to_file()
        self.refresh_notes_list()
        dialog.dismiss()
    
    def back_to_list(self):
        self.root.current = 'notes_list'
    
    def show_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()


if __name__ == '__main__':
    NotepadApp().run()