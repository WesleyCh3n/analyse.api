package handlers

import (
	"os"
	"path"
	"strconv"

	"analyze.api/app/models"
	"analyze.api/pkg/utils"

	"github.com/gofiber/fiber/v2"
)

// Export godoc
// @Summary      export selection files
// @Tags         Python
// @Description  return processed selection csv
// @ID           export_selection_file
// @Accept       application/json
// @Produce      application/json
// @Param        FltrFile    body      models.FltrFile  true  "filtered files"
// @Param        RangeIndex  body      []models.Range   true  "selected ranges"
// @Success      201         {object}  models.ResExport
// @Router       /api/export [put]
func Export(c *fiber.Ctx) error {
	reqBody := models.ReqExport{}
	if err := c.BodyParser(&reqBody); err != nil {
		return c.Status(fiber.StatusMethodNotAllowed).JSON(fiber.Map{
			"msg":  "Invalid request input",
			"data": nil,
		})
	}

	if err := os.MkdirAll(exportDir, os.ModePerm); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"msg":  err.Error(),
			"data": nil,
		})
	}

	// execute python
	exportFile := models.ExportFile{}
	app := analyzeExe
	args := []string{"export"}
	args = append(args,
		"-f", path.Join(filterDir, reqBody.Fltr.Rslt),
		"-s", exportDir)
	for _, r := range reqBody.Range {
		args = append(args, "-r",
			strconv.Itoa(int(r.Start))+" "+strconv.Itoa(int(r.End)))
	}
	if err := utils.CmdRunner(app, args, &exportFile); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"msg":  err.Error(),
			"data": nil,
		})
	}

	// create meta data and send to client
	data := models.ResExport{
		ServerRoot: serverRoot,
		SaveDir:    exportDir,
		Python:     exportFile,
	}

	return c.Status(fiber.StatusCreated).JSON(fiber.Map{
		"msg":  "Export successfully",
		"data": data,
	})
}

// Concat godoc
// @Summary      concat 2 selection csv
// @Tags         Python
// @Description  return concat selection csvs
// @ID           concat_selection_file
// @Accept       application/json
// @Produce      application/json
// @Param        files  body      []string  true  "files need to be concated"
// @Success      201    {object}  models.ResConcat
// @Router       /api/concat [put]
func Concat(c *fiber.Ctx) error {
	reqBody := models.ReqConcat{}
	if err := c.BodyParser(&reqBody); err != nil {
		return err
	}

	if err := os.MkdirAll(exportDir, os.ModePerm); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"msg":  err.Error(),
			"data": nil,
		})
	}
	// TODO: concat output name
	os.Remove("./file/export/concat.csv")

	// execute python
	concatFile := models.ConcatFile{}
	app := analyzeExe
	args := []string{"concat"}
	for _, r := range reqBody.Files {
		args = append(args, "-f", r)
	}
	args = append(args, "-s", exportDir)
	if err := utils.CmdRunner(app, args, &concatFile); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"msg":  err.Error(),
			"data": nil,
		})
	}

	data := models.ResConcat{
		ServerRoot: serverRoot,
		SaveDir:    exportDir,
		Python:     concatFile,
	}

	return c.Status(fiber.StatusCreated).JSON(fiber.Map{
		"msg":  "Concat successfully",
		"data": data,
	})
}

// SaveRange godoc
// @Summary      Save selected range in raw file
// @Tags         Python
// @Description  Save selected range in raw file
// @ID           save_selected_range
// @Accept       application/json
// @Produce      application/json
// @Param        UploadFile  body      string  true  "Original file"
// @Param        Range       body      string  true  "range(string)  to  write  in  csv  column"
// @Success      200         {object}  string  "Success message"
// @Router       /api/save [patch]
func SaveRange(c *fiber.Ctx) error {
	reqBody := models.ReqSave{}
	if err := c.BodyParser(&reqBody); err != nil {
		return err
	}

	// execute python
	cleanFile := models.CleanFile{}
	app := analyzeExe
	args := []string{"swrite"}
	args = append(args, "-f", path.Join(rawDir, reqBody.UploadFile))
	args = append(args, "-s", cleanDir)
	args = append(args, "-v", reqBody.Range)
	if err := utils.CmdRunner(app, args, &cleanFile); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"msg":  err.Error(),
			"data": nil,
		})
	}

	data := models.ResClean{
		ServerRoot: serverRoot,
		SaveDir:    cleanDir,
		Python:     cleanFile,
	}

	return c.Status(fiber.StatusOK).JSON(fiber.Map{
		"msg":  "Uploaded successfully",
		"data": data,
	})
}
