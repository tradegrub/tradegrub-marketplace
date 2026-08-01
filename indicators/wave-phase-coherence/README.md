# Wave Phase Coherence

![Concept](concept.svg)

Measures constructive and destructive interference between RSI oscillators at three timeframes (7, 14, 28). When all three oscillators align in the same direction, constructive interference signals a strong trend.

## How It Works

- Computes RSI at periods 7, 14, and 28
- Normalizes each RSI from 0-100 to -1..1 range
- Coherence is the product of all three normalized values (positive when aligned, negative when conflicting)
- Magnitude is the sum of absolute values representing total oscillator energy

## Parameters

No user-configurable inputs. Uses fixed RSI periods of 7, 14, and 28.

## Outputs

- **Coherence**: Green line showing alignment strength and direction
- **Magnitude**: Purple line showing total oscillator energy
- **Zero Line**: Gray baseline
- **Background**: Green shading for strong bullish coherence, red shading for strong bearish coherence

## Usage Notes

- Coherence above 0.3 indicates strong constructive bullish interference across timeframes
- Coherence below -0.3 indicates strong constructive bearish interference
- High magnitude with low coherence suggests conflicting signals across timeframes
- Use coherence direction to confirm trend entries
