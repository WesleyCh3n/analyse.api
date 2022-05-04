package handlers

import (
	"fmt"
	"os"

	"analyze.api/app/models"
	"analyze.api/pkg/utils"

	"github.com/gofiber/fiber/v2"
)

var serverRoot = os.Getenv("ROOT") + ":" + os.Getenv("PORT")
var analyzeExe = os.Getenv("ANALYZE_EXE")
var rawDir = os.Getenv("FILTER_DIR")
var filterDir = os.Getenv("RAW_DIR")
var exportDir = os.Getenv("EXPORT_DIR")
var cleanDir = os.Getenv("CLEAN_DIR")

// FilterData godoc
// @Summary      Create filtered files
// @Tags         Python
// @Description  upload raw csv and return filtered csvs
// @ID           upload_create_filtered_data
// @Accept       multipart/form-data
// @Produce      application/json
// @Param        file  formData  string  true  "Upload file"
// @Success      201   {object}  models.ResUpload
// @Router       /api/upload [post]
func FilterData(c *fiber.Ctx) error {

	file, err := c.FormFile("file")
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"msg":  err.Error(),
			"data": nil,
		})
	}

	// generate uploadFile from filename and extension
	uploadFile := file.Filename

	// make upload directory
	if err := os.MkdirAll(rawDir, os.ModePerm); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"msg":  err.Error(),
			"data": nil,
		})
	}

	// save file to upload path
	filePath := fmt.Sprintf("./%s/%s", rawDir, uploadFile)
	if err := c.SaveFile(file, filePath); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"msg":  err.Error(),
			"data": nil,
		})
	}

	// make filtered files directory
	if err := os.MkdirAll(filterDir, os.ModePerm); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"msg":  err.Error(),
			"data": nil,
		})
	}

	// execute python
	fltr := models.Fltr{}
	app := analyzeExe
	args := []string{"filter", "-f", filePath, "-s", filterDir}
	if err := utils.CmdRunner(app, args, &fltr); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"msg":  err.Error(),
			"data": nil,
		})
	}

	// create meta data and send to client
	// data := map[string]interface{}{
	// "uploadFile": uploadFile,
	// "serverRoot": serverRoot,
	// "saveDir":    fltrDir,
	// "python":     fltrFile,
	// }
	data := models.ResUpload{
		Upload:     uploadFile,
		ServerRoot: serverRoot,
		SaveDir:    filterDir,
		Python:     fltr,
	}

	return c.Status(fiber.StatusCreated).JSON(fiber.Map{
		"msg":  "Uploaded successfully",
		"data": data,
	})
}
