GRAPHDIR = graphs

.SUFFIXES: .deps .dot .pdf .clusters .tes

all: $(GRAPHDIR) all.pdf modules.pdf

raw.deps: $(ROOT)
	sfood -i $(ROOT) $(FOOD_FLAGS) > $@

modules.clusters: $(ROOT)
	ls -1d selvbetjening/* | sed s/.*\2.pyc?// > $@

modules.deps: modules.clusters raw.deps
	cat raw.deps | sfood-cluster -f modules.clusters > $@

all.pdf: raw.deps
	cat raw.deps | sfood-graph | dot -Tps | ps2pdf - $(GRAPHDIR)/$@

modules.pdf: modules.deps
	cat modules.deps | sfood-graph | dot -Tps | ps2pdf - $(GRAPHDIR)/$@

$(GRAPHDIR):
	mkdir $(GRAPHDIR)

clean:
	rm -f *.clusters *.dot *.pdf
	ls -1 *.deps | grep -v ^raw.deps | xargs rm -f

realclean: clean
	rm -f raw.deps

dependency-graph.pdf:
	sfood ./selvbetjening | sfood-graph  | dot -Tps | ps2pdf - > dependency-graph.pdf