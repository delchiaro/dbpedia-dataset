import copy

from artwork.artwork import ArtworkDataset


def artwork_dataset_filtering(artwork_dataset):
    # type: (ArtworkDataset) -> ArtworkDataset
    if not isinstance(artwork_dataset, ArtworkDataset):
        return None

    filtered_artworks = []
    for artwork in artwork_dataset.artworks:
        if artwork.getTitle() != "" and artwork.getAuthorName() != "":
            filtered_artworks.append(artwork)

    ret_dataset = copy.deepcopy(artwork_dataset)
    ret_dataset._artworks = filtered_artworks

    return filtered_artworks



# DATASET = "artwork_dataset.json"
# FILTERED_DATASET = "artwork_dataset_filtered.json"
# ad = ArtworkDataset()
# ad.loadJson(DATASET)
# good_dataset = artwork_dataset_filtering(ad)
# print "Number of good artworks: " + str(len(good_dataset.artworks))
# good_dataset.saveJson(FILTERED_DATASET)