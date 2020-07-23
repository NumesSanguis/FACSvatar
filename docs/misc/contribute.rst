How to contribute
=================
Add new trackers, additional data processing capability, or add support your avatar creation software.

The main idea is that researchers/developers write their own micro modules with ZeroMQ and wrap them up as Docker containers.
Docker will make the modules OS independent and a default ZeroMQ interface let's these modules communicate with each other.
The ideal case is where a researcher/developer uploads a module, an other user downloads it, and he/she only has to add a few lines to ``docker-compose.yml`` to start using it.

* Image that you have created a better FACS value extracter. You only have to add a ZeroMQ component, and no modification is needed in the other modules or visualization. or
* You want to enable facial animation in Unreal. You only need to include a ZeroMQ subscriber component to your Unreal project and you can use the other modules as is.

By creating a repository of FACSvatar compatible modules, we can make more advanced Human-Agent Interaction (HAI) systems and don't have to start a project from scratch if we only want to focus on 1 component.
