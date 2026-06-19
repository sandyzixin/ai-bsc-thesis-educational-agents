# Files Not Included

Several virtual human components are not included in this public repository because they were provided by the supervisor and are not my own code to share publicly. In addition, some files containing private credentials, paid assets, or project specific implementation details were excluded too.

The following components are excluded:

* `Unity Project`: The Unity project used for the speech-enabled embodied virtual human interface. This project also contains paid assets and private implementation files.
* `speechToUnity.py`: Code used to connect the speech pipeline with the Unity virtual human.
* `utils.py`: Utility code for initializing Microsoft Azure Speech-to-Text.
* `config_azure.py`: Configuration file for Microsoft Azure services.
* `config_google.py`: Configuration file for Google services.
* `config_mistral.py`: Configuration file for Mistral API.
* `experiment_settings.py`: Configuration file containing experiment-specific settings.
* `mistral_prompt.py`: Code containing the Mistral prompt and functions used to generate LLM responses.
* `statements.py`: Code containing the Dutch and English statements, instructions, and follow-up questions used during the interaction.
* `.env`: Environment variables containing API keys and other private credentials.

