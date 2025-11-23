from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        self.tour_dao = TourDAO()

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """

        tour_attrazione = self.tour_dao.get_tour_attrazioni()

        for coppia in tour_attrazione:
            for tour in self.tour_map:
                if tour == coppia["id_tour"]:
                    self.tour_map[tour].attrazioni.add(coppia["id_attrazione"])
            for attrazione in self.attrazioni_map:
                if attrazione == coppia["id_attrazione"]:
                    self.attrazioni_map[attrazione].tour.add(coppia["id_tour"])

    def genera_pacchetto(self, id_regione, max_giorni, max_budget):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        self._ricorsione(id_regione, max_giorni, max_budget, [], 0, 0, 0, set())

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    @staticmethod
    def tour_accettabile(tour, attrazioni_usate):
        for attrazione in tour.attrazioni:
            if attrazione in attrazioni_usate:
                return False
        return True

    def _ricorsione(self, id_regione, max_giorni, max_budget, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""
        for tour in self.tour_map:
            tour = self.tour_map[tour]
            if tour.id_regione == id_regione:
                if durata_corrente + tour.durata_giorni <= max_giorni and costo_corrente + tour.costo <= max_budget:
                    if self.tour_accettabile(tour, attrazioni_usate):
                        pacchetto_parziale.append(tour)
                        valore_aggiunto = 0
                        for attrazione in tour.attrazioni:
                            attrazione = self.attrazioni_map[attrazione]
                            valore_aggiunto += attrazione.valore_culturale
                            attrazioni_usate.add(attrazione.id)
                        if valore_corrente + valore_aggiunto == self._valore_ottimo:
                            self._pacchetto_ottimo.append(pacchetto_parziale)
                        if valore_corrente + valore_aggiunto > self._valore_ottimo:
                            self._pacchetto_ottimo= []
                            self._valore_ottimo = valore_corrente + valore_aggiunto
                            self._pacchetto_ottimo.append(pacchetto_parziale)
                        self._ricorsione(id_regione,
                                         max_giorni,
                                         max_budget,
                                         pacchetto_parziale,
                                         durata_corrente + tour.durata_giorni,
                                         costo_corrente + tour.costo,
                                         valore_corrente + valore_aggiunto,
                                         attrazioni_usate)
                        pacchetto_parziale.pop()
                        durata_corrente -= tour.durata_giorni
                        costo_corrente -= tour.costo
                        valore_corrente -= valore_aggiunto
                        for attrazione in tour.attrazioni:
                            attrazione = self.attrazioni_map[attrazione]
                            attrazioni_usate.remove(attrazione.id)
