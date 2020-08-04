from .SampleAnnotation import SampleAnnotation
from .Submodules import AE, AS, MAE
from .ExportCounts import ExportCounts
from drop import utils
from pathlib import Path

class DropConfig:

    CONFIG_KEYS = [
        # wbuild keys
        "projectTitle", "htmlOutputPath", "scriptsPath", "indexWithFolderName", "fileRegex", "readmePath",
        # global parameters
        "root", "sampleAnnotation", "geneAnnotation", "genomeAssembly", "exportCounts", "tools",
        # modules
        "aberrantExpression", "aberrantSplicing", "mae"
    ]
    
    def __init__(self, wbuildConfig):
        """
        Parse wbuild/snakemake config object for DROP-specific content

        :param wbuildConfig: wBuild config object
        """

        self.wBuildConfig = wbuildConfig
        self.config_dict = self.setDefaults(wbuildConfig.getConfig())
        
        self.root = Path(self.get("root"))
        self.processedDataDir = self.root / "processed_data"
        self.processedResultsDir = self.root / "processed_results"
        utils.createDir(self.root)
        utils.createDir(self.processedDataDir)
        utils.createDir(self.processedResultsDir)

        self.htmlOutputPath = Path(self.get("htmlOutputPath"))
        self.readmePath = Path(self.get("readmePath"))

        self.geneAnnotation = self.get("geneAnnotation")
        self.genomeAssembly = self.get("genomeAssembly")
        self.sampleAnnotation = SampleAnnotation(self.get("sampleAnnotation"), self.root)

        # setup submodules
        cfg = self.config_dict
        sa = self.sampleAnnotation
        pd = self.processedDataDir
        pr = self.processedResultsDir
        self.AE = AE(cfg["aberrantExpression"], sa, pd, pr)
        self.AS = AS(cfg["aberrantSplicing"], sa, pd, pr)
        self.MAE = MAE(cfg["mae"], sa, pd, pr)

        self.exportCounts = ExportCounts(
            self.config_dict, self.processedResultsDir,
            self.sampleAnnotation, self.getGeneAnnotations(), self.get("genomeAssembly"),
            aberrantExpression=self.AE, aberrantSplicing=self.AS
        )

        # legacy
        utils.setKey(self.config_dict, None, "aberrantExpression", self.AE.dict_)
        utils.setKey(self.config_dict, None, "aberrantSplicing", self.AS.dict_)
        utils.setKey(self.config_dict, None, "mae", self.MAE.dict_)


    def setDefaults(self, config_dict):
        """
        Check mandatory keys and set defaults for any missing keys
        :param config_dict: config dictionary
        :return: config dictionary with defaults
        """
        # check mandatory keys
        config_dict = utils.checkKeys(config_dict, keys=["htmlOutputPath", "root", "sampleAnnotation"], check_files=True)
        config_dict["geneAnnotation"] = utils.checkKeys(config_dict["geneAnnotation"], keys=None, check_files=True)

        config_dict["indexWithFolderName"] = True
        config_dict["fileRegex"] = ".*\.R"
        config_dict["wBuildPath"] = utils.getWBuildPath()
        
        setKey = utils.setKey
        setKey(config_dict, None, "genomeAssembly", "hg19")

        # set submodule dictionaries
        setKey(config_dict, None, "aberrantExpression", dict())
        setKey(config_dict, None, "aberrantSplicing", dict())
        setKey(config_dict, None, "mae", dict())
        setKey(config_dict, None, "exportCounts", dict())

        # commandline tools
        setKey(config_dict, None, "tools", dict())
        setKey(config_dict, ["tools"], "samtoolsCmd", "samtools")
        setKey(config_dict, ["tools"], "bcftoolsCmd", "bcftools")
        setKey(config_dict, ["tools"], "gatkCmd", "gatk")
        
        return config_dict
    
    def getRoot(self, str_=True):
        return utils.returnPath(self.root, str_=str_)
    
    def getProcessedDataDir(self, str_=True):
        return utils.returnPath(self.processedDataDir, str_=str_)
    
    def getProcessedResultsDir(self, str_=True):
        return utils.returnPath(self.processedResultsDir, str_=str_)
    
    def getHtmlOutputPath(self, str_=True):
        return utils.returnPath(self.htmlOutputPath, str_=str_)

    def getHtmlFromScript(self, path):
        stump = self.htmlOutputPath / utils.getRuleFromPath(path, prefix=True)
        return str(stump) + ".html"
    
    def get(self, key):
        if key not in self.CONFIG_KEYS:
            raise KeyError(f"{key} not defined for Drop config")
        return self.wBuildConfig.get(key)

    def getGeneAnnotations(self):
        return self.geneAnnotation
        
    def getGeneVersions(self):
        return self.geneAnnotation.keys()
    
    def getGeneAnnotationFile(self, annotation):
        return self.geneAnnotation[annotation]
