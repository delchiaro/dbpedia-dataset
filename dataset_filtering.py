from artwork.artwork import ArtworkDataset
DATASET = "artwork_dataset.json"
FILTERED_DATASET = "artwork_dataset_goodquery.json"


def good_query_artworks(artwork_dataset):
    if not isinstance(artwork_dataset, ArtworkDataset):
        return None

    ret = []
    for artwork in artwork_dataset.artworks:
        if artwork.getTitle() != "" and artwork.getAuthorName() != "":
            ret.append(artwork)

    return ret

ad = ArtworkDataset()
ad.loadJson(DATASET)

good_artworks = good_query_artworks(ad)

print "Good query artworks: " + str(len(good_artworks))

ad.artworks = good_artworks
ad.saveJson(FILTERED_DATASET)