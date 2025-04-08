import spade
import asyncio
from acquisition_agent import AcquisitionAgent
from segmentation_agent import SegmentationAgent
from feature_agent import FeatureAgent
from decision_agent import DecisionAgent

async def main():
    a = AcquisitionAgent("acquirer@localhost", "pass")
    s = SegmentationAgent("segmenter@localhost", "pass")
    f = FeatureAgent("feature@localhost", "pass")
    d = DecisionAgent("decision@localhost", "pass")

    await a.start()
    await s.start()
    await f.start()
    await d.start()

    print("✅ All agents started. System running...")

    await a.stop_event.wait()

if __name__ == "__main__":
    spade.run(main())
