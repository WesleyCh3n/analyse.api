package handlers

import (
	"fmt"
	"log"
	"os"

	"github.com/gofiber/fiber/v2"
)

func Pong(c *fiber.Ctx) error {
	mkDir("./file/csv")
	mkDir("./file/raw")
	return c.Status(200).SendString("ok")
}

func mkDir(p string) (err error) {
	// newpath := filepath.Join()
	err = os.MkdirAll(p, os.ModePerm)
	return
}

func UploadFile(c *fiber.Ctx) error {
	// mkDir("./file/csv")
	// mkDir("./file/raw")
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

	// save image to ./file/csv dir
	serverOrigin := "http://localhost:3001"
	saveDir := "file/csv"
	filePath := fmt.Sprintf("./%s/%s", saveDir, uploadFile)
	err = c.SaveFile(file, filePath)

	if err != nil {
		log.Println("image save error --> ", err)
		return c.JSON(fiber.Map{
			"status":  500,
			"message": "Server error",
			"data":    nil,
		})
	}

	outList, err := runPython(filePath, saveDir)

	if err != nil {
		log.Println("cannot run python script", err)
		return c.JSON(fiber.Map{
			"status":  500,
			"message": "sub process error",
			"data":    nil,
		})
	}

	// generate image url to serve to client using CDN
	rsltUrl := fmt.Sprintf("%s/%s", serverOrigin, outList[0])
	cyclUrl := fmt.Sprintf("%s/%s", serverOrigin, outList[1])
	cyltUrl := fmt.Sprintf("%s/%s", serverOrigin, outList[2])
	cyrtUrl := fmt.Sprintf("%s/%s", serverOrigin, outList[3])
	cydbUrl := fmt.Sprintf("%s/%s", serverOrigin, outList[4])

	// create meta data and send to client

	data := map[string]interface{}{
		"imageName": uploadFile,
		"header":    file.Header,
		"size":      file.Size,
	}

	return c.JSON(fiber.Map{
		"status":  201,
		"message": "uploaded successfully",
		"rsltUrl": rsltUrl,
		"cyclUrl": cyclUrl,
		"cyltUrl": cyltUrl,
		"cyrtUrl": cyrtUrl,
		"cydbUrl": cydbUrl,
		"data":    data,
	})
}
