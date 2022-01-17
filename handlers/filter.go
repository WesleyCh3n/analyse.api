package handlers

import (
	"encoding/json"
	"fmt"
	"os/exec"
)

type CsvPathJson struct {
	Result string `json:"Result"`
	CyGt   string `json:"CyGt"`
	CyLt   string `json:"CyLt"`
	CyRt   string `json:"CyRt"`
	CyDb   string `json:"CyDb"`
}

func getFilteredData(csvFile, outDir string) (CsvPathJson, error) {
	cmd := exec.Command("./scripts/filter.py", "-f", csvFile, "-s", outDir)
	stdout, err := cmd.Output()

	resultPath := CsvPathJson{}
	if err != nil {
		fmt.Println(err.Error())
		return resultPath, err
	}

	json.Unmarshal(stdout, &resultPath)

	return resultPath, err
}
