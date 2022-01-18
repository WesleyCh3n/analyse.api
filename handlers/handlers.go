package handlers

import (
	"fmt"
	"log"
	"os"

	"github.com/gofiber/fiber/v2"
)

var serverRoot = "http://localhost:3001"

func Pong(c *fiber.Ctx) error {
	return c.Status(200).SendString("ok")
}

func mkDir(p string) (err error) {
	err = os.MkdirAll(p, os.ModePerm)
	return
}

func UploadFile(c *fiber.Ctx) error {
	file, err := c.FormFile("file")

	if err != nil {
		log.Println("upload error --> ", err)
		return c.JSON(fiber.Map{
			"status":  500,
			"message": "Server error",
			"data":    nil,
		})
	}

	// generate uploadFile from filename and extension
	uploadFile := file.Filename

	// save upload file to ./file/csv dir
	uploadDir := "file/raw"
	mkDir(uploadDir)
	filePath := fmt.Sprintf("./%s/%s", uploadDir, uploadFile)
	err = c.SaveFile(file, filePath)
	if err != nil {
		log.Println("image save error --> ", err)
		return c.JSON(fiber.Map{
			"status":  500,
			"message": "Server error",
			"data":    nil,
		})
	}

	saveDir := "file/csv"
	mkDir(saveDir)
	filteredData, err := getFilteredData(filePath, saveDir)

	if err != nil {
		log.Println("cannot run python script", err)
		return c.JSON(fiber.Map{
			"status":  500,
			"message": "sub process error",
			"data":    nil,
		})
	}

	// create meta data and send to client
	data := map[string]interface{}{
		"uploadFile": uploadFile,
		"prefix":     fmt.Sprintf("%s/%s", serverRoot, saveDir),
		"python":     filteredData,
	}

	return c.JSON(fiber.Map{
		"status":  201,
		"message": "Uploaded successfully",
		"data":    data,
	})
}

func Export(c *fiber.Ctx) error {
	result := ReqExport{}

	if err := c.BodyParser(&result); err != nil {
		log.Println(err)
		return err
	}

	saveDir := "file/export"
	mkDir(saveDir)
	exportData, err := exportCsv(result, saveDir)
	if err != nil {
		log.Println("Python script error", err)
		return c.JSON(fiber.Map{
			"status":  500,
			"message": "Sub process error",
			"data":    err,
		})
	}

	data := map[string]interface{}{
		"prefix": fmt.Sprintf("%s/%s", serverRoot, saveDir),
		"python": exportData,
	}

	return c.JSON(fiber.Map{
		"status":  201,
		"message": "Export complete",
		"data":    data,
	})
}
