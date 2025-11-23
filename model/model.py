import numpy

from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo = -1
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
    def tour_accettabile(tour, durata_corrente, costo_corrente, max_giorni, max_budget, attrazioni_usate, tour_usati):
        if max_giorni is None:
            max_giorni = numpy.inf
        if max_budget is None:
            max_budget = numpy.inf

        if durata_corrente + tour.durata_giorni <= max_giorni and costo_corrente + tour.costo <= max_budget:
            for attrazione in tour.attrazioni:
                if attrazione in attrazioni_usate:
                    return False
            if tour in tour_usati:
                return False
            return True
        return False

    def _ricorsione(self, id_regione, max_giorni, max_budget, pacchetto_parziale, durata_corrente, costo_corrente, valore_corrente, attrazioni_usate):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""
        for tour in self.tour_map:
            tour = self.tour_map[tour]
            if tour.id_regione == id_regione:
                if self.tour_accettabile(tour, durata_corrente, costo_corrente, max_giorni, max_budget, attrazioni_usate, pacchetto_parziale):
                    pacchetto_parziale.append(tour)
                    durata_corrente += tour.durata_giorni
                    costo_corrente += tour.costo
                    for attrazione in tour.attrazioni:
                        attrazioni_usate.add(attrazione)
                        valore_corrente += self.attrazioni_map[attrazione].valore_culturale

                    if valore_corrente > self._valore_ottimo:
                        self._pacchetto_ottimo = pacchetto_parziale.copy()
                        self._valore_ottimo = valore_corrente
                        self._costo = costo_corrente

                    self._ricorsione(id_regione, max_giorni, max_budget, pacchetto_parziale, durata_corrente, costo_corrente, valore_corrente, attrazioni_usate)

                    pacchetto_parziale.pop()
                    durata_corrente -= tour.durata_giorni
                    costo_corrente += tour.costo
                    for attrazione in tour.attrazioni:
                        attrazioni_usate.difference(attrazione)
                        valore_corrente -= self.attrazioni_map[attrazione].valore_culturale
