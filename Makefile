
clean:
	rm svgs/*


svgs/%.svg: recipies/%.dot
	echo $<
	dot -Tsvg <$< >$@
