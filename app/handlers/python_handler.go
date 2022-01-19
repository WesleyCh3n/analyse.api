package handlers

import (
	"os"
	"server/app/models"
	"server/pkg/utils"
	"strconv"

	"github.com/gofiber/fiber/v2"
)

// Export godoc
// @Summary      export selection files
// @Tags Export
// @Description  return processed selection csv
// @ID           export_selection_file
// @Accept       application/json
// @Produce      application/json
// @Param FltrFile body models.FltrFile true "filtered files"
// @Param Range body []models.Range true "selected ranges"
// @Success      201  {object}  models.ExportFile
// @Router       /api/export [post]
func Export(c *fiber.Ctx) error {
	reqBody := struct {
		Fltr  models.FltrFile `json:"FltrFile"`
		Range []models.Range  `json:"Range"`
	}{}
	if err := c.BodyParser(&reqBody); err != nil {
		return c.Status(fiber.StatusMethodNotAllowed).JSON(fiber.Map{
			"msg":  "Invalid request input",
			"data": nil,
		})
	}

	saveDir := "file/export"
	if err := os.MkdirAll(saveDir, os.ModePerm); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"msg":  err.Error(),
			"data": nil,
		})
	}

	// execute python
	exportFile := models.ExportFile{}
	app := "./scripts/exporter.py"
	args := []string{}
	for _, r := range reqBody.Range {
		args = append(args, "-r", strconv.Itoa(r.Start), strconv.Itoa(r.End))
	}
	args = append(args, "-f", reqBody.Fltr.Rslt, "-c", reqBody.Fltr.CyGt, "-s", saveDir)
	if err := utils.CmdRunner(app, args, &exportFile); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"msg":  err.Error(),
			"data": nil,
		})
	}

	// create meta data and send to client
	data := map[string]interface{}{
		"serverRoot": serverRoot,
		"saveDir":    saveDir,
		"python":     exportFile,
	}

	return c.Status(fiber.StatusCreated).JSON(fiber.Map{
		"msg":  "Export successfully",
		"data": data,
	})
}

// Concat godoc
// @Summary      concat 2 selection csv
// @Tags Concat
// @Description  return concat selection csvs
// @ID           concat_selection_file
// @Accept       application/json
// @Produce      application/json
// @Param Files body []string true "files need to be concated"
// @Success      201  {object}  models.ConcatFile
// @Router       /api/concat [post]
func Concat(c *fiber.Ctx) error {
	reqBody := struct {
		Files []string `json:"files"`
	}{}
	if err := c.BodyParser(&reqBody); err != nil {
		return err
	}

	saveDir := "file/export"
	if err := os.MkdirAll(saveDir, os.ModePerm); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"msg":  err.Error(),
			"data": nil,
		})
	}

	// execute python
	concatFile := models.ConcatFile{}
	app := "./scripts/concater.py"
	args := []string{"-f"}
	for _, r := range reqBody.Files {
		args = append(args, r)
	}
	args = append(args, "-s", saveDir)
	if err := utils.CmdRunner(app, args, &concatFile); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"msg":  err.Error(),
			"data": nil,
		})
	}

	data := map[string]interface{}{
		"serverRoot": serverRoot,
		"saveDir":    saveDir,
		"python":     concatFile,
	}

	return c.Status(fiber.StatusCreated).JSON(fiber.Map{
		"msg":  "Concat successfully",
		"data": data,
	})
}
