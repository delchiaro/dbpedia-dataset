from argparse import ArgumentParser

from artwork.artwork import ArtworkDataset

DATASET_PATH = "./dataset"
RESULT_DATASET = "./data/artwork_dataset.json"




def show_uri_info(uri):
    ad = ArtworkDataset()
    ad.loadJson(RESULT_DATASET)

    art_dict = dict ((x.getFolderName(), x) for x in ad.artworks)
    print unicode(art_dict[uri].getStrRepr(True, True, True))




if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-u", "-uri", action='store', dest='uri', default=None,
                        help="Insert the uri of which display info stored in the dataset")

    args = parser.parse_args()

    if args.uri is not None:
        show_uri_info(args.uri.decode("UTF-8"))
    else:
        parser.print_usage()