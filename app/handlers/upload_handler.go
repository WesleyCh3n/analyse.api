package handlers

import (
	"fmt"
	"os"
	"server/app/models"
	"server/pkg/utils"

	"github.com/gofiber/fiber/v2"
)

var serverRoot = "http://localhost:3001"

// FilterData godoc
// @Summary      Create filtered files
// @Tags Filter
// @Description  upload raw csv and return filtered csvs
// @ID           upload_create_filtered_data
// @Accept       multipart/form-data
// @Produce      application/json
// @Param file formData string true "Upload file"
// @Success      201  {object}  models.FltrFile
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
	uploadDir := "file/raw"
	if err := os.MkdirAll(uploadDir, os.ModePerm); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"msg":  err.Error(),
			"data": nil,
		})
	}

	// save file to upload path
	filePath := fmt.Sprintf("./%s/%s", uploadDir, uploadFile)
	if err := c.SaveFile(file, filePath); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"msg":  err.Error(),
			"data": nil,
		})
	}

	// make filtered files directory
	saveDir := "file/csv"
	if err := os.MkdirAll(saveDir, os.ModePerm); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"msg":  err.Error(),
			"data": nil,
		})
	}

	// execute python
	fltrFile := models.FltrFile{}
	app := "./scripts/filter.py"
	args := []string{"-f", filePath, "-s", saveDir}
	if err := utils.CmdRunner(app, args, &fltrFile); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"msg":  err.Error(),
			"data": nil,
		})
	}

	// create meta data and send to client
	data := map[string]interface{}{
		"uploadFile": uploadFile,
		"serverRoot": serverRoot,
		"saveDir":    saveDir,
		"python":     fltrFile,
	}

	return c.Status(fiber.StatusCreated).JSON(fiber.Map{
		"msg":  "Uploaded successfully",
		"data": data,
	})
}
