"use client";

import Link from "next/link";
import { MoonIcon, SunIcon } from "@radix-ui/react-icons";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardFooter,
  CardTitle,
} from "@/components/ui/card";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"

import { useToast } from "@/components/ui/use-toast"
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

import {
  InputOTP,
  InputOTPGroup,
  InputOTPSeparator,
  InputOTPSlot,
} from "@/components/ui/input-otp";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import React, { useEffect } from 'react';
import axios from 'axios';
import { useState } from 'react';
import Cookies from 'js-cookie';
export default function LoginForm() {
  const { setTheme } = useTheme();
  const [songTitle, setSongTitle] = useState('');
  const [songArtist, setSongArtist] = useState('');
  const [bitrate, setBitrate] = useState('');
  const [audioType, setAudioType] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showSearchResults, setshowSearchResults] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState('');
  const [showAlert, setShowAlert] = useState(false);
  const [apiEndpoint, setApiEndpoint] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  let endpoint = '';
  const { toast } = useToast()

  function normalizeEndpoint(endpoint) {
    // Check if the endpoint is a non-empty string
    if (typeof endpoint === 'string' && endpoint.length > 0) {
      // Replace 'https' with 'http'
      endpoint = endpoint.replace(/^https:/i, 'http:');
  
      // // Check if the last character is not a forward slash
      // if (endpoint.charAt(endpoint.length - 1) !== '/') {
      //   // Append a forward slash to the endpoint
      //   endpoint += '/';
      // }
    }
    toast({
      title: "API endpoint set!",
      description: `${endpoint}`,
    })
    return endpoint
  }

  useEffect(() => {
    const storedApiEndpoint = Cookies.get('apiEndpoint');
    if (storedApiEndpoint) {
      endpoint = normalizeEndpoint(storedApiEndpoint);

      setApiEndpoint(endpoint);
    } else {
      setShowDialog(true);
    }
  }, []);

  const handleSubmit = () => {
    const endpoint2 = document.getElementById('apiendpoint').value;
    endpoint = normalizeEndpoint(endpoint2)
    
    setApiEndpoint(`${endpoint}`);
    Cookies.set('apiEndpoint', `${endpoint}`, { expires: 365 }); // Set cookie to expire in 1 year
    setShowDialog(false);
  };
  const handleDownload = async (e:any) => {
    e.preventDefault();
    setIsLoading(true);

  
    try {
      const response = await axios.get(`${apiEndpoint}/download_song`, {
        params: {
          song_name: songTitle,
          song_artist: songArtist,
          bitrate: bitrate,
          audio_type: audioType,
        },
      });
      console.log('Download successful:', response.data.url);
      toast({
        title: "Download Successful",
        description: songTitle + ' has been downloaded successfully. Thank you for using Song Downloader!',
      })
      setDownloadUrl(response.data.url);
      setShowAlert(true);
    } catch (error:str) {
        console.error('Error downloading song:', error);
        toast({
          title: "Error downloading song",
          description: error.message,
        })
    } finally {
      setIsLoading(false);
    }
  };


  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${apiEndpoint}/search?query=${query}`);
        const data = await response.json();
        setSearchResults(data);
      } catch (error) {
        console.error('Error fetching search results:', error);
      }
    };

    if (query.trim() !== '') {
      fetchData();
    } else {
      setSearchResults({});
    }
  }, [query]);

  const handleQueryChange = any => {
    const inputElement = document.getElementById('song');
    const inputText = inputElement.value;
    setQuery(inputText);
    setshowSearchResults(true)
  };

  const setdownload = (name, artist, album, duration) => {
    console.log(artist)
    const songTitle = document.getElementById('song-title').value = name;
    const songArtist = document.getElementById('song-artist').value = artist;
    // const inputElement = document.getElementById('song-artist').value = artist;
    setBitrate("=320")
    setSongTitle(name)
    setSongArtist(artist)
    setshowSearchResults(false)
  };

  function msToMinutesAndSeconds(ms) {
    const minutes = Math.floor(ms / 60000); // Get the number of full minutes
    const seconds = Math.floor((ms % 60000) / 1000); // Get the remaining seconds
  
    // Format the output string
    const minutesStr = minutes.toString().padStart(2, '0');
    const secondsStr = seconds.toString().padStart(2, '0');
  
    return `${minutesStr}:${secondsStr}`;
  }

  const renderTableRows = () => {
    return Object.entries(searchResults).map(([name, [artist, album, duration]]) => (
      <TableRow key={name} onClick={() => { setdownload(name, artist, album, duration); }}>
        <TableCell className="font-medium">{name}</TableCell>
        <TableCell>{artist}</TableCell>
        <TableCell>{album}</TableCell>
        <TableCell className="text-right">{duration}</TableCell>
      </TableRow>
    ));
  };

  return (
    <>
      <center>
      {showDialog && (
        <AlertDialog open={showDialog}>
          <AlertDialogTrigger>Open</AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Enter API Endpoint</AlertDialogTitle>
              <AlertDialogDescription>
                Please enter the API endpoint for your application.
              </AlertDialogDescription>
              <Input
                        id="apiendpoint"
                        placeholder="http://*.*.*.*:8000/"
                        type="text"
 
                      />
            </AlertDialogHeader>
            <AlertDialogFooter>
              {/* <AlertDialogCancel onClick={() => setShowDialog(false)}>Cancel</AlertDialogCancel> */}
              <AlertDialogAction onClick={() => handleSubmit()}>Continue</AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      )}
        <div style={{ marginBottom: "20px", marginTop: "10px" }}>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="icon">
                <SunIcon className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
                <MoonIcon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
                <span className="sr-only">Toggle theme</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => setTheme("light")}>
                Light
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme("dark")}>
                Dark
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme("system")}>
                System
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </center>
      <center>
        <Tabs defaultValue="simple" className="w-[400px]">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="simple">Simple</TabsTrigger>
            <TabsTrigger value="advanced">Advanced</TabsTrigger>
          </TabsList>
          <TabsContent value="simple">
            <Card className="mx-auto max-w-sm">
              <CardHeader>
                <CardTitle className="text-xl">Song Downloader</CardTitle>
                <CardDescription>
                  Song Downloader (simple) allows you to download every song in high quality.
                </CardDescription>
              </CardHeader>
              <CardContent>
              <div style={{marginBottom: "3vh"}} className="grid gap-2">
                      <Label htmlFor="search">Search (press enter to search)</Label>
                      <Input
                        id="song"
                        placeholder="Blue Monday"
                        type="text"
 
                        onKeyDown={(e) => {if (e.key === 'Enter') {
                          handleQueryChange()
                          
                        }}}
                        
                      />

                    </div>
                    <div style={{ marginTop: "3vh", marginBottom: "3vh" }}>
                    <Label htmlFor="search">Or enter manualy</Label>
                  </div>
                <div className="grid gap-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label htmlFor="song-title">Song Title</Label>
                      <Input
                        id="song-title"
                        placeholder="Blue Monday"
                        type="text"
 
                        required
                      />

                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="song-artist">Song Artist</Label>
                      <Input
                        id="song-artist"
                        placeholder="New Order"
                        // value={songArtist}
                        onChange={(e) => setSongArtist(e.target.value)}
                        required
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="first-name">Bitrate</Label>
                        <Select value={bitrate} onValueChange={setBitrate}>
                          <SelectTrigger className="">
                            <SelectValue placeholder="Select Bitrate" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="=320">320 kbps</SelectItem>
                            <SelectItem value=">192 <320">
                              {">"}192 {"<"}320 kbps
                            </SelectItem>
                            <SelectItem value="=128">128 kbps</SelectItem>
                          </SelectContent>
                        </Select>
                    </div>
                    <div className="grid gap-2">
                    <Label htmlFor="first-name">Audio type</Label>
                        <Select value={audioType} onValueChange={setAudioType}>
                          <SelectTrigger className="">
                            <SelectValue placeholder="mp3" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="mp3">mp3</SelectItem>
                            <SelectItem value="flac">
                              flac
                            </SelectItem>
                          </SelectContent>
                        </Select>
                    </div>
                  </div>
                  
                  <div style={{ marginTop: "10px", marginBottom: "30px" }}>
                    <Separator />
                  </div>
                  
                    <AlertDialog open={showSearchResults}>
                      {/* <AlertDialogTrigger>Open</AlertDialogTrigger> */}
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Search results for "{`${query}`}"</AlertDialogTitle>
                          <AlertDialogDescription>
                            Please select the song you want to download by pressing on it. Then change the settings if needed and hit "Download"
                          </AlertDialogDescription>
                          <Table>
                            
                            <TableHeader>
                              <TableRow>
                                <TableHead className="w-[100px]">Name</TableHead>
                                <TableHead>Artist</TableHead>
                                <TableHead>Album</TableHead>
                                <TableHead className="text-right">Duration</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>{renderTableRows()}</TableBody>
                          </Table>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <Button onClick={() => { setshowSearchResults(false); }}>Cancel</Button>
                          {/* <AlertDialogAction>Continue</AlertDialogAction> */}
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                    <Button type="button" onClick={handleDownload} className="w-full" disabled={isLoading}>
                      {isLoading ? 'Downloading...' : 'Download (.mp3)'}
                    </Button>
                      
                      <AlertDialog open={showAlert}>
                        <AlertDialogTrigger hidden>Open</AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Download Successful</AlertDialogTitle>
                            <AlertDialogDescription>
                            {songTitle} has been downloaded successfully.
                            Thank you for using Song Downloader!
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <a href={downloadUrl} download>
                              <Button>Download</Button>
                            </a>
                            {/* <AlertDialogAction>Continue</AlertDialogAction> */}
                            <AlertDialogCancel onClick={() => { setShowAlert(false); setDownloadUrl(''); }}>
                              Close
                            </AlertDialogCancel>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                  
                </div>
                <div className="mt-4 text-center text-sm">
                  Having issues?{" "}
                  <Link href="#" className="underline">
                    Submit a bug report
                  </Link>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="advanced">
            <center>
              <Card className="mx-auto max-w-sm">
                <CardHeader>
                  <CardTitle className="text-xl">
                    Song Downloader (advanced)
                  </CardTitle>
                  <CardDescription>
                  Song Downloader (advanced) allows you to download entier Spotify playlists in high quality.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4">
                    <div className="">
                      <Label htmlFor="first-name">Bitrate</Label>
                      <Select>
                        <SelectTrigger className="w-[180px]">
                          <SelectValue placeholder="Select Bitrate" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="light">320 kbps</SelectItem>
                          <SelectItem value="dark">
                            {">"}192 {"<"}320 kbps
                          </SelectItem>
                          <SelectItem value="system">128 kbps</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="password">Spotify url</Label>
                      <Input placeholder="https://open.spotify.com/playlist/" />
                    </div>
                    <div style={{ marginTop: "10px", marginBottom: "30px" }}>
                      <Separator />
                    </div>
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button type="submit" className="w-full">
                          Download (.zip)
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>You are in the queue...</DialogTitle>
                          <DialogDescription>
                            <div style={{ marginTop: "10px" }}>
                              <Progress value={33} />
                            </div>
                          </DialogDescription>
                        </DialogHeader>
                      </DialogContent>
                    </Dialog>
                  </div>
                  <div className="mt-4 text-center text-sm">
                    Having issues?{" "}
                    <Link href="#" className="underline">
                      Submit a bug report
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </center>
          </TabsContent>
        </Tabs>
      </center>

    </>
  );
}
