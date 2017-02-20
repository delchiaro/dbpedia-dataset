import json
import os
import shutil
from flickrDownloader import *

from utils import todict


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

    def getQuery(self):
        query = self.getTitle()
        if self.getAuthorName() != "":
            query += " " + self.getAuthorName
        return query

    def getFolderName(self):  # type: (Artwork) -> str
        if self.uri is None:
            return None
        else:
            return self.uri.replace("/", "^")

    @staticmethod
    def folderNameToUri(str):  # type: (str) -> str
        return str.split("/")[-1].replace("/", "^")



class ArtworkDataset:

    def __init__(self, img_path="./dataset", seed_prefix="dbpseed_", gimg_prefix="google_", flickr_prefix="flickr_"):
        self._artworks = []
        self._datasetPath = "./dataset"

    def retriveDbPediaThumbs(self):
        pass


    @property
    def artworks(self):
        return self._artworks





    def findArtworkByFolderName(self, folder_name, print_warning=True, error_for_warning=False):
        uri = Artwork.folderNameToUri(folder_name)
        finded = filter(lambda a: a.uri == uri, self.artworks)

        if len(finded) == 0:
            return None
        else:
            if len(finded) > 1:
                if print_warning:
                    print("Warning: more than one artwork finded")
                if error_for_warning:
                    raise RuntimeError("More than one artwork finded")
            return finded


    def destroyImageDataset(self):
        if os.path.isdir(self._datasetPath):
            shutil.rmtree(self._datasetPath)

    def retriveGoogleImages(self, images_per_artwork=5, verbose=True, print_warnings=True, deep_verbose=True):
        from googleImageDownloader import google_image_download

        artwork_without_uri = []
        artwork_without_query = []
        n_downloads = 0
        print("##########################################################################################")
        print("###############  G O O G L E    I M A G E S    D O W N L O A D I N G  ####################")
        print("##########################################################################################")
        os.makedirs(self._datasetPath)

        for artwork in self.artworks:

            if artwork.uri is None:
                artwork_without_uri.append(artwork)
                if print_warnings or verbose:
                    print("* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * ")
                    print("Warning: artwork without uri info")
                    print("Artwork Title  = {}".format(artwork.getTitle()))
                    print("Artwork Author = {}".format(artwork.getAuthorName()))
                    print("* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * ")
                    print("\n")
            else:

                if verbose:
                    print("* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * ")
                    print("Downloading google images for:")
                    print("Artwork Title  = {}".format(artwork.getTitle()))
                    print("Artwork Author = {}".format(artwork.getAuthorName()))
                    print("Artwork Uri    = {}".format(artwork.uri))


                query = artwork.getQuery()
                if query == "":
                    print("Warning: no info to make a query!! Can't retrive google images.")
                    artwork_without_query.append(artwork)
                else:
                    path = os.path.join(self._datasetPath, artwork.getFolderName())
                    l = google_image_download(search_keyword=query,
                                              n_downloads=images_per_artwork,
                                              extension_blacklist=[".gif", ".png", ".svg"],
                                              extension_whitelist=[".jpg", ".jpeg"],
                                              replace_extension_not_in_whitelist=".jpg",
                                              download_img_path=path,
                                              image_file_prefix=artwork.getFolderName() + "_google_",
                                              verbose=(deep_verbose and verbose),
                                              print_warnings=print_warnings)
                    n_downloads += len(l)

                if verbose:
                    print("* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * ")
                    print("\n")

        if verbose:
            print("##########################################################################################")
            print("DONE!")
            print("Downloaded images -----------------> {}".format(n_downloads))
            print("Artwork without URI warnings ------> {}".format(len(artwork_without_uri)))
            print("Artwork without query warnings ----> {}".format(len(artwork_without_query)))
            print("##########################################################################################")



    def retriveFlickrImages(self, images_per_artwork=5, verbose=True, print_warnings=True, deep_verbose=True):
        api_key = "flickr.apikey"
        artwork_without_uri = []
        artwork_without_query = []
        n_downloads = 0
        print("##########################################################################################")
        print("###############  F L I C K R    P H O T O S    D O W N L O A D I N G  ####################")
        print("##########################################################################################")
        os.makedirs(self._datasetPath)

        for artwork in self.artworks:

            if artwork.uri is None:
                artwork_without_uri.append(artwork)
                if print_warnings or verbose:
                    print("* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * ")
                    print("Warning: artwork without uri info")
                    print("Artwork Title  = {}".format(artwork.getTitle()))
                    print("Artwork Author = {}".format(artwork.getAuthorName()))
                    print("* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * ")
                    print("\n")
            else:

                if verbose:
                    print("* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * ")
                    print("Downloading google images for:")
                    print("Artwork Title  = {}".format(artwork.getTitle()))
                    print("Artwork Author = {}".format(artwork.getAuthorName()))
                    print("Artwork Uri    = {}".format(artwork.uri))


                query = artwork.getQuery()
                if query == "":
                    print("Warning: no info to make a query!! Can't retrive google images.")
                    artwork_without_query.append(artwork)
                else:
                    path = os.path.join(self._datasetPath, artwork.getFolderName())
                    l = flickr_photos_downloader(api_key_or_file_path=api_key,
                                                 query_text=query,
                                                 n_images=n_downloads,
                                                 content_type=FlickrContentType.photos,
                                                 media=FlickrMedia.photos,
                                                 image_size=FlickrImageSize.longedge_640,
                                                 download_path=path,
                                                 save_filename_prefix=artwork.getFolderName() + "_flickr_",
                                                 verbose=(deep_verbose and verbose),
                                                 ignore_errors=not print_warnings)
                    n_downloads += len(l)

                if verbose:
                    print("* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * ")
                    print("\n")

        if verbose:
            print("##########################################################################################")
            print("DONE!")
            print("Downloaded images -----------------> {}".format(n_downloads))
            print("Artwork without URI warnings ------> {}".format(len(artwork_without_uri)))
            print("Artwork without query warnings ----> {}".format(len(artwork_without_query)))
            print("##########################################################################################")


    def retriveDbPediaThumbs(self):
        import urllib


        os.makedirs(self._datasetPath)

        i = 0
        duplicati = []
        non_duplicati = []
        for artwork in self.artworks:
            print i
            art_path = os.path.join(self._datasetPath, artwork.getFolderName())
            if os.path.isdir(art_path):
                duplicati.append(artwork)

            else:
                non_duplicati = []
                os.makedirs(art_path)
                artwork_img_link = artwork.getThumbLink(500)
                if artwork_img_link is not None:
                    filename = artwork.getAuthorName() + "-" + artwork.getTitle() + "-seed_w500.jpg"
                    urllib.urlretrieve(urllib.unquote(artwork_img_link.encode('utf8', ':/')), art_path + "/" + filename)
            i += 1

        print "duplicati: " + str(len(duplicati))

        json_str = json.dumps(todict(duplicati))
        json_file = open("duplicati.json", "w")
        json_file.write(json_str)
        json_file.close()

        print "non duplicati: " + str(len(non_duplicati))

        json_str = json.dumps(todict(non_duplicati))
        json_file = open("dataset_non_duplicati.json", "w")
        json_file.write(json_str)
        json_file.close()


    def remove_duplicate(self):
        pass

    def saveJson(self, out_json_path):
        if out_json_path is not None:
            json_str = json.dumps(todict(self.artworks))
            json_file = open(out_json_path, "w")
            json_file.write(json_str)
            json_file.close()
            return True
        else:
            return False

    def loadJson(self):
        pass

    def saveImagesHDF5(self):
        pass

    def uri2artwork_map(self):
        pass

