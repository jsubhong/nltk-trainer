import argparse
import nltk.corpus
from nltk.corpus.util import LazyCorpusLoader
from nltk.probability import FreqDist
from nltk.tag.simplify import simplify_wsj_tag
from nltk_trainer.tagging import readers

########################################
## command options & argument parsing ##
########################################

parser = argparse.ArgumentParser(description='Analyze a part-of-speech tagged corpus',
	formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('corpus',
	help='''The name of a tagged corpus included with NLTK, such as treebank,
brown, cess_esp, floresta, or the root path to a corpus directory,
which can be either an absolute path or relative to a nltk_data directory.''')
parser.add_argument('--trace', default=1, type=int,
	help='How much trace output you want, defaults to %(default)d. 0 is no trace output.')

corpus_group = parser.add_argument_group('Corpus Reader Options')
corpus_group.add_argument('--reader', default=None,
	help='''Full module path to a corpus reader class, such as
nltk.corpus.reader.tagged.TaggedCorpusReader''')
corpus_group.add_argument('--fileids', default=None,
	help='Specify fileids to load from corpus')
corpus_group.add_argument('--simplify_tags', action='store_true', default=False,
	help='Use simplified tags')

sort_group = parser.add_argument_group('Tag Count Sorting Options')
sort_group.add_argument('--sort', default='tag', choices=['tag', 'count'],
	help='Sort key, defaults to %(default)s')
sort_group.add_argument('--reverse', action='store_true', default=False,
	help='Sort in revere order')

args = parser.parse_args()

###################
## corpus reader ##
###################

tagged_corpus = readers.load_corpus_reader(args.corpus, reader=args.reader, fileids=args.fileids)

if not tagged_corpus:
	raise ValueError('%s is an unknown corpus')

if args.trace:
	print 'loading nltk.corpus.%s' % args.corpus

##############
## counting ##
##############

wc = 0
tag_counts = FreqDist()
word_set = set()

if args.corpus in ['conll2000', 'switchboard']:
	kwargs = {}
else:
	kwargs = {'simplify_tags': args.simplify_tags}

for word, tag in tagged_corpus.tagged_words(**kwargs):
	if args.corpus in ['conll2000', 'switchboard'] and args.simplify_tags:
		tag = simplify_wsj_tag(tag)
	
	wc += 1
	tag_counts.inc(tag)
	word_set.add(word)

############
## output ##
############

print '%d total words\n%d unique words\n%d tags\n' % (wc, len(word_set), len(tag_counts))

if args.sort == 'tag':
	sort_key = lambda (t, c): t
elif args.sort == 'count':
	sort_key = lambda (t, c): c
else:
	raise ValueError('%s is not a valid sort option' % args.sort)

# simple reSt table format
print '  Tag  \t  Count  '
print '=======\t========='

for tag, count in sorted(tag_counts.items(), key=sort_key, reverse=args.reverse):
	print '%s\t%s' % (tag, count)

print '=======\t========='