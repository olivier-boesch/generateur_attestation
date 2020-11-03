#!/usr/bin/python3
# coding: utf8
from kivy.app import App
from kivy.factory import Factory
from kivy.logger import Logger
from kivy.storage.jsonstore import JsonStore
from gen_pdf import motifs_courts, generer_pdf
import os.path
from kivy import platform
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path, app_storage_path
    from android import loadingscreen
    data_dir = app_storage_path()
    user_dir = primary_external_storage_path()
else:
    from pathlib import Path
    data_dir = os.path.dirname(os.path.abspath(__file__))
    user_dir = Path.home()
    import locale
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

__version__ = "0.9.8"


class AttgenApp(App):
    data = {'nom': '',
            'prenom': '',
            'date_naissance': '',
            'lieu_naissance': '',
            'adresse': '',
            'code_postal': '',
            'commune': '',
            'motif_defaut': '1',
            'motif_help': '5',
            'decalage_help': '20'}

    def show_settings_popup(self):
        p = Factory.SettingsPopup()
        p.open()
        for k in self.data.keys():
            if 'motif' in k:
                p.ids[k].text = motifs_courts[int(self.data[k])]
            else:
                try:
                    p.ids[k].text = self.data[k]
                except KeyError:
                    pass

    def on_dismiss_settings_popup(self, pop):
        for k in self.data.keys():
            try:
                if 'motif' in k:
                    self.data[k] = motifs_courts.index(pop.ids[k].text)
                else:
                    self.data[k] = pop.ids[k].text
            except KeyError:
                pass

    def show_about(self):
        p = Factory.AboutPopup()
        p.open()

    def load_data(self):
        Logger.info("Data: Loading data...")
        store = JsonStore(os.path.join(data_dir, 'data.json'))
        for k in store.keys():
            self.data[k] = store.get(k)['val']
        Logger.info("Data: Loading data done {:s}".format(str(self.data)))

    def save_data(self):
        Logger.info("Data: Saving data...")
        store = JsonStore(os.path.join(data_dir, 'data.json'))
        for k in self.data.keys():
            store.put(k, val=str(self.data[k]))
        Logger.info("Data: Saving data done")

    def generer_urgence(self):
        self.generer(urgence=True)

    def generer(self, urgence=False):
        if platform == 'android':
            ret = request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
        try:
            if not urgence:
                motif = int(self.root.cur_motif)
            else:
                motif = int(self.data['motif_help'])
            name = generer_pdf(save_dir=user_dir, data=self.data, motif=motif, urgence=urgence)
            if platform == 'android':
                pass
            else:
                import webbrowser
                webbrowser.open_new(os.path.join(user_dir, name))
        except PermissionError:
            pass

    def on_start(self):
        self.load_data()
        self.root.ids['motif'+str(self.data['motif_defaut'])].state = 'down'
        loadingscreen.hide_loading_screen()

    def on_stop(self):
        self.save_data()
        
    def on_pause(self):
        self.save_data()
        
    def on_resume(self):
        self.load_data()


if __name__ == "__main__":
    app = AttgenApp()
    app.run()
