"""Plugin registry for embedded video URL resolution."""

from .base import VideoCandidate
from .known_hosts import DailymotionResolver, YouTubeResolver, VimeoResolver, default_final_resolvers
from .players import DramaVideoResolver, FastVidResolver, GenericIframeResolver, default_player_resolvers

__all__ = [
    "VideoCandidate",
    "DailymotionResolver", "YouTubeResolver", "VimeoResolver",
    "FastVidResolver", "DramaVideoResolver", "GenericIframeResolver",
    "default_final_resolvers", "default_player_resolvers",
]
