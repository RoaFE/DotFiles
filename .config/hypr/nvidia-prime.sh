#!/bin/bash

PROFILE=$(powerprofilesctl get)

if [ "$PROFILE" = "performance" ] || [ "$PROFILE" = "balanced" ]; then
	export __NV_PRIME_RENDER_OFFLOAD=1
	export __VK_LAYER_NV_optimus=NVIDIA_only
	export __GLX_VENDOR_LIBRARY_NAME=nvidia
fi

