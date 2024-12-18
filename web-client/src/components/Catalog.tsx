import React, { useEffect, useState } from "react";

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"

interface CatalogProps {
  onLocateObject: (object: string[]) => void;
}

const Catalog = ({ onLocateObject }: CatalogProps) => {
  const [data, setData] = useState<string[][]>([]);
  const [celestialObjects, setCelestialObjects] = useState<string[]>([]);
  const [selectedObject, setSelectedObject] = useState<string>("");

  useEffect(() => {
    fetch("messier_catalog.csv")
      .then((response) => response.text())
      .then((csvText) => {
        const parsedData = parseCSV(csvText);
        setData(parsedData);

        const objects = parsedData.slice(1).map((row) => row[0]);
        setCelestialObjects(objects);
      })
      .catch((error) => console.error("Error fetching the CSV file:", error));
  }, []);

  const parseCSV = (csv: string): string[][] => {
    const rows = csv.trim().split("\n");

    return rows.map((row) => {
      const fields: string[] = [];
      let currentField = "";
      let inQuotes = false;

      for (let i = 0; i < row.length; i++) {
        const char = row[i];

        if (char === '"' && (i === 0 || row[i - 1] !== "\\")) {
          inQuotes = !inQuotes;
        } 
        else if (char === "," && !inQuotes) {
          fields.push(currentField.trim());
          currentField = "";
        } 
        else {
          currentField += char;
        }
      }

      fields.push(currentField.trim());
      return fields;
    });
  };

  const handleStartTracking = () => {
    if (selectedObject) {
      const selectedRow = data.find((row) => row[0] === selectedObject);
    
      if (!selectedRow) {
        console.error(`No data found for object: ${selectedObject}`);
        return;
      }
      onLocateObject(selectedRow);
    } else {
      console.error("No celestial object selected");
    }
  };

    return (
      <div>
        <Card>
          <CardHeader>
            <form>
              <div className="grid w-full items-center gap-4">
                <div className="flex flex-col space-y-1.5">
                  <Label htmlFor="framework">SELECT A CELESTIAL OBJECT</Label>
                  <Select onValueChange={(value) => setSelectedObject(value)}>
                    <SelectTrigger id="framework">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent position="popper">
                      {celestialObjects.map((object, index) => (
                        <SelectItem key={index} value={object}>
                          {object}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Button onClick={handleStartTracking}>Start Tracking</Button>
              </div>
            </form>  
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[58vh] rounded-md border p-4">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[100px]">M</TableHead>
                    <TableHead>NGC</TableHead>
                    <TableHead>TYPE</TableHead>
                    <TableHead>CONSTELLATION</TableHead>
                    <TableHead>RIGHT ASCENSION</TableHead>
                    <TableHead>DECLINATION</TableHead>
                    <TableHead>MAGNITUDE</TableHead>
                    <TableHead>SIZE</TableHead>
                    <TableHead>DISTANCE (LIGHT YEARS)</TableHead>
                    <TableHead>VIEWING SEASON</TableHead>
                    <TableHead>VIEWING DIFFICULTY</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.slice(1).map((row, rowIndex) => (
                    <TableRow key={rowIndex}>
                      {row.map((cell, cellIndex) => (
                        <TableCell key={cellIndex}>{cell}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <ScrollBar orientation="horizontal" />
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    )
};

export default Catalog;