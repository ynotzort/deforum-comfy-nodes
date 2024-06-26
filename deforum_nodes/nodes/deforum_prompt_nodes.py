import torch

from nodes import MAX_RESOLUTION
from ..modules.deforum_node_base import DeforumDataBase

class DeforumPromptNode(DeforumDataBase):
    def __init__(self):
        super().__init__()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompts": ("STRING", {"forceInput": False, "multiline": True, "default": "0:'Cat Sushi'"}),
            },
            "optional": {
                "deforum_data": ("deforum_data",),
            },
        }

    RETURN_TYPES = (("deforum_data",))
    FUNCTION = "get"
    OUTPUT_NODE = True
    CATEGORY = f"deforum/prompt"
    display_name = "Prompt"

    @torch.inference_mode()
    def get(self, prompts, deforum_data=None):
        if deforum_data and "prompts" in deforum_data:
            # Convert the formatted prompts back to a string for editing
            formatted_prompts = deforum_data["prompts"]
            prompts = "\n".join([f"{key}:'{value}'" for key, value in formatted_prompts.items()])
        else:
            # Splitting the data into rows
            rows = prompts.split('\n')

            # Creating an empty dictionary
            prompts_dict = {}

            # Parsing each row
            for row in rows:
                key, value = row.split(':', 1)
                key = int(key)
                value = value.strip('"')
                prompts_dict[key] = value

            if deforum_data:
                deforum_data["prompts"] = prompts_dict
            else:
                deforum_data = {"prompts": prompts_dict}

        return (deforum_data,)


class DeforumAreaPromptNode(DeforumDataBase):

    default_area_prompt = '[{"0": [{"prompt": "a vast starscape with distant nebulae and galaxies", "x": 0, "y": 0, "w": 1024, "h": 1024, "s": 0.7}, {"prompt": "detailed sci-fi spaceship", "x": 512, "y": 512, "w": 50, "h": 50, "s": 0.7}]}, {"50": [{"prompt": "a vast starscape with distant nebulae and galaxies", "x": 0, "y": 0, "w": 1024, "h": 1024, "s": 0.7}, {"prompt": "detailed sci-fi spaceship", "x": 412, "y": 412, "w": 200, "h": 200, "s": 0.7}]}, {"100": [{"prompt": "a vast starscape with distant nebulae and galaxies", "x": 0, "y": 0, "w": 1024, "h": 1024, "s": 0.7}, {"prompt": "detailed sci-fi spaceship", "x": 112, "y": 112, "w": 800, "h": 800, "s": 0.7}]}]'
    default_prompt = "Alien landscape"

    def __init__(self):
        super().__init__()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "keyframe": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 1}),
                "mode":(["default", "percentage", "strength"],),
                "prompt": ("STRING", {"forceInput": False, "multiline": True, 'default': cls.default_prompt,}),
                "width": ("INT", {"default": 64, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                "height": ("INT", {"default": 64, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                "x": ("INT", {"default": 0, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
                "y": ("INT", {"default": 0, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01}),
            },
            "optional": {
                "deforum_data": ("deforum_data",),
            },
        }

    RETURN_TYPES = (("deforum_data",))
    FUNCTION = "get"
    OUTPUT_NODE = True
    CATEGORY = f"deforum/prompt"
    display_name = "Area Prompt"

    @torch.inference_mode()
    def get(self, keyframe, mode, prompt, width, height, x, y, strength, deforum_data=None):

        area_prompt = {"prompt": prompt, "x": x, "y": y, "w": width, "h": height, "s": strength, "mode":mode}
        area_prompt_dict = {f"{keyframe}": [area_prompt]}

        if not deforum_data:
            deforum_data = {"area_prompts":[area_prompt_dict]}

        if "area_prompts" not in deforum_data:
            deforum_data["area_prompts"] = [area_prompt_dict]
        else:

            added = None

            for item in deforum_data["area_prompts"]:
                for k, v in item.items():
                    if int(k) == keyframe:
                        if area_prompt not in v:
                            v.append(area_prompt)
                            added = True
                        else:
                            added = True
            if not added:
                deforum_data["area_prompts"].append(area_prompt_dict)

        deforum_data["prompts"] = None

        return (deforum_data,)


class DeforumUnformattedPromptNode(DeforumDataBase):
    def __init__(self):
        super().__init__()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "unformatted_prompts": ("STRING", {"forceInput": False, "multiline": True}),
                "keyframe_interval": ("INT", {"default": 50, "min": 1, "max": 8192, "step": 1}),
            },
            "optional": {
                "deforum_data": ("deforum_data",),
            },
        }

    RETURN_TYPES = (("deforum_data",))
    FUNCTION = "get"
    OUTPUT_NODE = True
    CATEGORY = f"deforum/prompt"
    display_name = "Unformatted Prompt"

    @torch.inference_mode()
    def get(self, unformatted_prompts, keyframe_interval, deforum_data=None):
        # Splitting the unformatted prompts into lines
        lines = unformatted_prompts.split('\n')

        # Creating an empty dictionary for formatted prompts
        formatted_prompts = {}

        # Parsing each line and formatting the prompts
        for i, line in enumerate(lines):
            keyframe = i * keyframe_interval
            formatted_prompts[keyframe] = line.strip()

        if deforum_data:
            deforum_data["prompts"] = formatted_prompts
        else:
            deforum_data = {"prompts": formatted_prompts}

        return (deforum_data,)

class DeforumAppendNode(DeforumDataBase):
    def __init__(self):
        super().__init__()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "append_text": ("STRING", {"multiline": True, "default": ""}),
                "keyframe_interval": ("INT", {"default": 50, "min": 1, "max": 8192, "step": 1}),
            },
            "optional": {
                "deforum_data": ("deforum_data",),
                "append_to_all": (["No", "Yes"], {"default": "No"}),
                "use_neg": (["No", "Yes"], {"default": "No"}),
            },
        }

    RETURN_TYPES = (("deforum_data",))
    FUNCTION = "get"
    OUTPUT_NODE = True
    CATEGORY = f"deforum/prompt"
    display_name = "Append"

    @torch.inference_mode()
    def get(self, append_text, keyframe_interval, deforum_data=None, append_to_all="No", use_neg="No"):
        print("Append Text:", append_text)
        print("Keyframe Interval:", keyframe_interval)
        print("Deforum Data:", deforum_data)
        print("Append to All:", append_to_all)
        print("Use --neg:", use_neg)
        
        if deforum_data and "prompts" in deforum_data:
            formatted_prompts = deforum_data["prompts"]
            print("Formatted Prompts (Before Append):", formatted_prompts)
            
            neg_prefix = "--neg " if use_neg == "Yes" else ""
            
            if append_to_all == "Yes":
                # Append the first line of append_text to every prompt
                first_line = append_text.split('\n')[0]
                for key in formatted_prompts:
                    formatted_prompts[key] = f"{formatted_prompts[key]} {neg_prefix}{first_line}"
            else:
                # Append the append_text to prompts based on keyframe interval
                lines = append_text.split('\n')
                for i, line in enumerate(lines):
                    keyframe = i * keyframe_interval
                    if keyframe in formatted_prompts:
                        formatted_prompts[keyframe] = f"{formatted_prompts[keyframe]} {neg_prefix}{line}"
            
            print("Formatted Prompts (After Append):", formatted_prompts)
            deforum_data["prompts"] = formatted_prompts
        else:
            deforum_data = {"prompts": {}}

        return (deforum_data,)
