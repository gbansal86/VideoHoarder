from pathlib import Path

path = Path(__file__).with_name("build_full_adapted_spec.py")
source = path.read_text(encoding="utf-8")

start = source.index('r=p.add_run("DESIGN REVIEW SET')
end = source.index("\n\nconcepts=[", start)
selected_intro = '''r=p.add_run("SELECTED DESIGN - SIDEBAR COMMAND CENTER  ");set_font(r,bold=True,color=TEAL,size=8.8)
r=p.add_run("This is the approved primary application shell for ChatGPT Processing. The four non-selected concepts are retained in a separate design-alternatives document for future reference.");set_font(r,size=8.8)'''
source = source[:start] + selected_intro + source[end:]

start = source.index('doc.add_heading("80.6 Recommended Direction"')
end = source.index("\n\n# Styling and page furniture.", start)
selected_direction = '''doc.add_heading("80.2 Implementation Direction",level=2)
doc.add_paragraph("Implement the Sidebar Command Center as the primary ChatGPT Processing shell. Keep its persistent navigation, manual-exchange notice, six-stage workflow, status counters, current-work list and quick actions. The four alternate concepts are intentionally excluded from this master specification and preserved separately as optional future references.")'''
source = source[:start] + selected_direction + source[end:]

path.write_text(source, encoding="utf-8")
