
generate-templates:
	python generate-template.py

%.pdf: %.svg
	rsvg-convert -f pdf --output "$@" "$^"

templates: templates/*.pdf

.PHONY: templates
