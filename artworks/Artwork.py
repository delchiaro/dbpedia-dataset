
class LatLng:
    def __init__(self):
        self.lat = None
        self.lng = None


class Author:
    def __init__(self):
        self.name = None
        self.uri = None
        self.nationality = None
        self.birthLocations = []
        self._birthLatLng = None
        self.birthYear = None
        self.deathYear = None

    @property
    def birthLatLng(self):
        return self._birthLatLng

    @birthLatLng.setter
    def birthLatLng(self, latLng):
        # type: (LatLng) -> None
        self._birthLatLng = latLng


class Museum:
    def __init__(self):
        self.uri = None
        self.name = []
        self.latLng = None
        self.locations = []

    @property
    def latLng(self):
        return self._latlng

    @latLng.setter
    def latLng(self, latLng):
        # type: (LatLng) -> None
        self._latlng = latLng



class Artwork:
    def __init__(self):
        self.uri = None
        self.title = None
        self.thumb_link = None
        self.img_link = None

        self.comment = []
        self.description = []
        #self.creationYear = None
        self.currentLatLng = LatLng
        #self.creationLatLng = LatLng
        self.currentLocations = []
        self.creationLocations = []

        self._museums = []
        self._authors = []


    def addAuthor(self, author):
        # type: (Author) -> None
        self._authors.append(author)
        return

    def addMuseum(self, museum):
        # type: (Museum) -> None
        self._museums.append(museum)
        return

    @property
    def museums(self):
        return self.museums

    @property
    def authors(self):
        return self.authors




