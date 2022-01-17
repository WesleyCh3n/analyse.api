package handlers

import (
	"fmt"
	"log"
	"os"

	"github.com/gofiber/fiber/v2"
)

func Pong(c *fiber.Ctx) error {
	// getFilteredData("./file/raw/2021-09-26-18-36_ultium_motion_Dr Tsai_2021.09.26 Dr. Tsai_1.csv", "./scripts/")
	return c.Status(200).SendString("ok")
}

func mkDir(p string) (err error) {
	err = os.MkdirAll(p, os.ModePerm)
	return
}

func UploadFile(c *fiber.Ctx) error {
	mkDir("./file/csv")
	mkDir("./file/raw")
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
	serverRoot := "http://localhost:3001"
	uploadDir := "file/raw"
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
	path, err := getFilteredData(filePath, saveDir)

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
		"UploadFile": uploadFile,
		"header":     file.Header,
		"size":       file.Size,
		"rsltUrl":    fmt.Sprintf("%s/%s", serverRoot, path.Result),
		"cyclUrl":    fmt.Sprintf("%s/%s", serverRoot, path.CyGt),
		"cyltUrl":    fmt.Sprintf("%s/%s", serverRoot, path.CyLt),
		"cyrtUrl":    fmt.Sprintf("%s/%s", serverRoot, path.CyRt),
		"cydbUrl":    fmt.Sprintf("%s/%s", serverRoot, path.CyDb),
	}

	return c.JSON(fiber.Map{
		"status":  201,
		"message": "uploaded successfully",
		"data":    data,
	})
}

func Export(c *fiber.Ctx) error {
	result := ReqExport{}

	if err := c.BodyParser(&result); err != nil {
		log.Println(err)
		return err
	}

	exportCsv(result)

	return c.JSON(fiber.Map{
		"status":  201,
		"message": "Export complete",
	})
}
