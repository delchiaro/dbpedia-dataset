from artwork.artwork import ArtworkDataset


DATASET_PATH = "./dataset/dataset_new/"
RESULT_DATASET = "artwork_dataset_goodquery.json"
OUTPUT_TXT = "documents.txt"



def main():
    doc_processing =  lambda str: str.replace('\n', '')
    prepare_docs(OUTPUT_TXT, doc_processing)

def prepare_docs(out_file, lambda_on_doc_str=None):
    ad = ArtworkDataset(img_path=DATASET_PATH)
    ad.loadJson(RESULT_DATASET)

    outf = file(out_file, mode='w')

    for artwork in ad.artworks:
        title = artwork.title
        descr = artwork.description
        comment = artwork.comment
        authors = artwork.authors
        #locations = artwork.currentLocations



        if comment is None:
            comment = u''
        if descr is None:
            descr = u''
        if title is None:
            title = u''

        authors_str = u""
        if authors is not None:
            for author in authors:
                if author.name is not None:
                    authors_str += u"Author Name: " + author.name + u". "
                if author.comment is not None:
                    authors_str += author.comment + u". "
                if author.abstract is not None:
                    authors_str += author.abstract + u". "

                if author.birthDate is not None:
                    authors_str += u"Author Birth: " + str(author.birthDate)
                if author.deathDate is not None:
                    authors_str += u", Author Death: " + str(author.deathDate) + u'. '
                else:
                    authors_str += '. '

                if author.movement is not None:
                    authors_str += u"Author Movement: " + author.movement + u'. '

                if author.nationality is not None:
                    authors_str += u"Author Nationality: " + author.nationality + u'. '

        locations_str = u""
        # if locations is not None:
        #     for loc in locations:
        #         authors_str += str(loc)

        doc = title + u'. ' + authors_str + '. ' + comment + '. ' + descr +'. ' + locations_str
        # doc.replace('\n', '')
        if lambda_on_doc_str is not None:
            doc = lambda_on_doc_str(doc)
        doc += u'\n'
        outf.write(doc.encode("UTF-8"))

    outf.close()


if __name__ == "__main__":
    main()