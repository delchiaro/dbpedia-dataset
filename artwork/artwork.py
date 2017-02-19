
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

        self.comment = None
        self.description = None
        #self.creationYear = None
        self.currentLatLng = LatLng
        #self.creationLatLng = LatLng
        self.currentLocations = None
        self.creationLocations = None

        self._museums = None
        self._authors = None

    def getTitle(self):
        if self.title is not None:
            return self.title
        else:
            return "<unknown-title>"

    def getAuthorName(self):
        if self.authors is not None:
            if self.authors[0].name is not None:
                return self.authors[0].name
        else:
            return "<unknown-author>"

    def addAuthor(self, author):
        # type: (Author) -> None
        if self._authors is None:
            self._authors = [author]
        else:
            self._authors.append(author)
        return

    def addMuseum(self, museum):
        # type: (Museum) -> None
        if self._museums is None:
            self._museums = [museum]
        else:
            self._museums.append(museum)
        return

    @property
    def museums(self):
        return self._museums

    @property
    def authors(self):
        return self._authors

    def getThumbLink(self, resize_width=None):
        if resize_width is None:
            if self.img_link is not None:
                return self.img_link

        if self.thumb_link is not None:
            split = self.thumb_link.split("?width=")
            if len(split) > 0:
                return split[0] + "?width=" + (str(resize_width) if resize_width is not None else "")

        return self.thumb_link







class ArtworkDataset:

    def __init__(self, img_path, seed_prefix="dbpseed_", gimg_prefix="google_", flickr_prefix="flickr_"):
        self._artworks = []

    def retriveDbPediaThumbs(self):
        pass

    def retriveGoogleImages(self):
        pass

    def retriveFlickrImages(self):
        pass

    def remove_duplicate(self):
        pass

    def saveJson(self):
        pass  # TODO:

    def loadJson(self):
        pass

    def saveImagesHDF5(self):
        pass

    def uri2artwork_map(self):
        pass

