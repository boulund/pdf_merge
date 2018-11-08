#!/usr/bin/env python3
"""Merge PDF documents: put several documents per page."""
__author__ = "Fredrik Boulund"
__date__ = "2018-04-27"

from sys import argv, exit
import argparse
from itertools import zip_longest

from pdfrw import PdfReader, PdfWriter, PageMerge, IndirectPdfDict

def grouper(n, iterable, fillvalue=None):
    """Group iterable into sets of n.
    Standard Python itertools recipe.
    """
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def parse_args():
    desc = "{doc} Copyright (c) {author} {date}.".format(
            doc=__doc__,
            author=__author__,
            date=__date__[:4],
    )
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("PDF", nargs="+",
            help="PDF documents to merge")
    parser.add_argument("-o", "--outfile", 
            default="merged.pdf",
            help="Output filename [%(default)s].")
    parser.add_argument("-r", "--rows", type=int,
            default=2,
            help="Number of rows per page [%(default)s].")
    parser.add_argument("-c", "--cols", type=int,
            default=3,
            help="Number of cols per page [%(default)s].")
    parser.add_argument("-l", "--landscape", action="store_true", 
            default=False,
            help="Output pages in landscape orientation [%(default)s].")
    parser.add_argument("-t", "--title", 
            default="Merged PDF",
            help="PDF metadata: Title [%(default)s].")

    if len(argv) < 2:
        parser.print_help()
        exit(1)

    return parser.parse_args()


def put_pages_on_grid(pages, rows=2, cols=3):
    """Put pages on a grid on a single page."""
    scale = 1 / max(rows, cols)
    source_pages = PageMerge() + pages
    x_increment, y_increment = (scale * i for i in source_pages.xobj_box[2:])
    for page in source_pages:
        page.scale(scale)
        if i & 1:
            page.x = x_increment
        else:
            page.x = 0
        if i & 2:
            page.y = 0
        else:
            page.y = y_increment
    return source_pages.render()


def main(infiles, outfile, rows, cols, title, landscape):
    pages = []
    for pdf in infiles:
        pages.extend(PdfReader(pdf).pages)
    pages_per_page = rows * cols

    pdf_writer = PdfWriter(outfile)

    for page_group in grouper(pages_per_page, pages):
        pdf_writer.addpage(put_pages_on_grid(page_group, rows, cols))

    pdf_writer.trailer.Info = IndirectPdfDict(
            Title=title,
            Author="StaG-mwc",
            Creator=__file__)

    return pdf_writer


if __name__ == "__main__":
    args = parse_args()
    main(args.PDF, args.outfile, args.rows, args.cols, args.title, args.landscape)





