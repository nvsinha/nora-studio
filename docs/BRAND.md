# Nora brand marks

Four products, one system. Each mark is a node graph whose *topology* says what
that product does to a network — so they read as a family without being four
recolours of the same shape.

<!-- pyml disable no-inline-html,line-length -->
| | product | topology | says |
| --- | --- | --- | --- |
| <img src="https://raw.githubusercontent.com/nvsinha/nora-fleet/main/docs/logo.svg" width="40" height="40" alt="" /> | **nora-fleet** | hub with three spokes | radiates — one coordinator, many workers |
| <img src="https://raw.githubusercontent.com/nvsinha/nora-flow/main/docs/logo.svg" width="40" height="40" alt="" /> | **nora-flow** | a single directed path | traverses — moves through the network |
| <img src="https://raw.githubusercontent.com/nvsinha/nora-studio/main/docs/images/logo.svg" width="40" height="40" alt="" /> | **nora-studio** | a closed diamond circuit | encloses — the complete thing you author |
| <img src="https://raw.githubusercontent.com/nvsinha/nora-common/main/docs/logo.svg" width="40" height="40" alt="" /> | **nora-common** | two rings, intersection filled | overlaps — the shared part |

<!-- pyml enable no-inline-html,line-length -->

`nora-common` deliberately breaks the pattern. It is a library, not a service,
and drawing it as a network would claim something untrue about it.

## Palette

The same four accents the architecture diagram uses, so the marks and the docs
agree.

| product | accent |
| --- | --- |
| nora-fleet | `#3F9E88` |
| nora-flow | `#5B8CC4` |
| nora-studio | `#8A7BC8` |
| nora-common | `#C9A24A` |

All four are mid-tones on purpose: each clears its background on white and on
the app's `#131218` alike, so one file works everywhere and there is no
light/dark pair to keep in sync.

## Two variants

**`logo.svg` — the mark.** Single colour, transparent ground. Use at 32px and
up: READMEs, docs, slides. Single colour rather than accent-plus-grey, because
a two-tone mark reads as unfinished and does not survive being printed,
inverted, or dropped on an unknown background.

**`icon.svg` — the tile.** The mark reversed out of a filled rounded square.
Use below 32px, and anywhere the mark needs its own ground: favicons, app
icons, a title bar. This variant exists because a stroked node graph cannot
hold contrast at 16px on an unknown background — the tile gives it one.

## Geometry

A 64×64 artboard with a 44px live area. Connectors are 3.25 (flow's single
curve 3.5); nodes are 9 primary and 6.5 secondary. Round caps and joins
throughout. Edges are drawn first and nodes painted over them, so no line ever
pokes through a dot.

The connectors are deliberately half the node weight. The dots are the network;
the lines only say which of them are joined, so giving both the same weight
made the marks read as tangles rather than as graphs.

That thinness is also why the tile exists. Below about 24px a 3.25 stroke on an
unknown background stops holding contrast, and no amount of care in the mark
fixes that — the tile gives it a ground instead.

## Where the files are

    nora-fleet/docs/logo.svg          nora-fleet/docs/icon.svg
    nora-flow/docs/logo.svg           nora-flow/docs/icon.svg
    nora-studio/docs/images/logo.svg  nora-studio/docs/images/icon.svg
    nora-common/docs/logo.svg         nora-common/docs/icon.svg

nora-flow ships the tile twice more, and both are copies rather than imports:

    nora_flow/frontend/public/favicon.svg          the browser tab
    nora_flow/frontend/src/components/BrandMark.tsx  the app header

They are inline so they cannot flash or 404 while loading. If the geometry
changes, change all three.
