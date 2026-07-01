# Daily Percent Levels

Draws horizontal price levels at fixed percentage intervals above and below a reference price. The reference price is the close of the first visible bar.

## Conceptual Diagram

![Concept](concept.svg)

## What it shows

- A solid gray reference line at the starting price
- Green dashed lines above at each percentage step (+0.5%, +1.0%, +1.5%, etc.)
- Red dashed lines below at each percentage step (-0.5%, -1.0%, -1.5%, etc.)
- Labels on each line showing the percentage offset and exact price

## Inputs

- **Number of Levels:** how many percentage steps to draw above and below the reference (default 6, range 2 to 10)
- **Step Percent:** the percentage increment between each level (default 0.5%, range 0.1% to 2.0%)

## Use cases

- Quickly gauge how far price has moved from the session open in percentage terms
- Identify potential support and resistance zones based on round percentage moves
- Useful for intraday trading where percentage moves matter more than absolute price
