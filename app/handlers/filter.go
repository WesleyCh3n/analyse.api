package handlers

import (
	"encoding/json"
	"fmt"
	"os/exec"
	"server/app/models"
)

func getFilteredData(csvFile, outDir string) (models.FltrFile, error) {
	cmd := exec.Command("./scripts/filter.py", "-f", csvFile, "-s", outDir)
	stdout, err := cmd.Output()

	resultPath := models.FltrFile{}
	if err != nil {
		fmt.Println(err.Error())
		return resultPath, err
	}

	json.Unmarshal(stdout, &resultPath)

	return resultPath, err
}
