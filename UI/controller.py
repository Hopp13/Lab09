import flet as ft
from UI.view import View
from model.model import Model


class Controller:
    def __init__(self, view: View, model: Model):
        self._model = model
        self._view = view

        # Variabili per memorizzare le selezioni correnti
        self.regione_selezionata = None
        self.durata = None
        self.costo = None

    def on_regione_change(self, e):
        """Aggiorna la regione selezionata e salva il valore."""
        self.regione_selezionata = e.control.value

    def popola_dropdown_regione(self):
        """Popola il menu a tendina delle regioni."""
        self._view.dd_regione.options.clear()

        regioni = self._model.load_regioni() # Ogni regione (id, nome_regione)

        if regioni:
            for regione in sorted(regioni):
                self._view.dd_regione.options.append(ft.dropdown.Option(key=regione.id,text=regione.nome))
        else:
            self._view.show_alert("Errore nel caricamento delle regioni.")

        self._view.update()

    def check_giorni(self, e):
        """Controlla che il formato sia corretto per durata in giorni"""
        try:
            self._view.durata_massima.error_text = None
            if e.control.value == "":
                self.durata = None
            else:
                self.durata = int(e.control.value)
        except Exception:
            self.durata = None
            self._view.durata_massima.error_text = "Giorni non Validi"
        self._view.update()

    def check_budget(self, e):
        """Controlla che il formato sia corretto per budget in euro"""
        try:
            self._view.budget_massimo.error_text = None
            if e.control.value == "":
                self.costo = None
            else:
                e.control.value = e.control.value.replace(".", "")
                self.costo = float(e.control.value.replace(",", "."))
        except Exception:
            self.costo = None
            self._view.budget_massimo.error_text = "Budget non valido"
        self._view.update()

    def genera_pacchetto(self, e):
        """Chiama il Model per generare il pacchetto ottimo"""
        if self.regione_selezionata is None:
            self._view.show_alert("Selezionare una Regione!")
        else:
            pacchetto, costo, val_culturale = self._model.genera_pacchetto(self.regione_selezionata,self.durata,self.costo)
            costo = f"{costo:.2f}".replace(".", ",")
            self._view.lista_visualizzazione.controls.clear()
            self._view.lista_visualizzazione.controls.append(
                ft.Text(f"Il pacchetto ottimo costa {costo}€ e ha valore culturale pari a {val_culturale}:"))
            for tour in pacchetto:
                self._view.lista_visualizzazione.controls.append(ft.Text(f" •    {tour} → {tour.attrazioni}"))
            self._view.update()
