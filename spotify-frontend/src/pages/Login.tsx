import { Button, Heading, Text, Flex, Image, Box, VStack } from '@chakra-ui/react';
import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState } from 'react';

const tracks = [
  // English
  {
    title: 'Blinding Lights',
    artist: 'The Weeknd',
    cover: 'https://i.scdn.co/image/ab67616d00001e028863bc11d2aa12b54f5aeb36', 
  },
  {
    title: 'Levitating',
    artist: 'Dua Lipa',
    cover: 'https://i.scdn.co/image/ab67616d0000b2734bc66095f8a70bc4e6593f4f', 
  },
  {
    title: 'Peaches',
    artist: 'Justin Bieber',
    cover: 'https://i.scdn.co/image/ab67616d0000b273e6f407c7f3a0ec98845e4431', 
  },
  {
    title: 'Save Your Tears',
    artist: 'The Weeknd',
    cover: 'https://i.scdn.co/image/ab67616d00001e028863bc11d2aa12b54f5aeb36', 
  },
  // Hindi
  {
    title: 'Tum Hi Ho',
    artist: 'Arijit Singh',
    cover: 'https://i.scdn.co/image/ab67616d0000b2736404721c1943d5069f0805f3',
  },
  {
    title: 'Apna Bana Le',
    artist: 'Arijit Singh',
    cover: 'https://i.scdn.co/image/ab67616d0000b273c7b32b2ebd1ed948c9e7e5c5',
  },
  {
    title: 'Kesariya',
    artist: 'Arijit Singh',
    cover: 'https://i.scdn.co/image/ab67616d0000b273c08202c50371e234d20caf62',
  },
  {
    title: 'Tum Ho',
    artist: 'Mohit Chauhan',
    cover: 'https://i.scdn.co/image/ab67616d0000b27354e544672baa16145d67612b',
  },
  {
    title: 'Falak Tak',
    artist: 'Udit Narayan, Mahalakshmi Iyer',
    cover: 'https://i.scdn.co/image/ab67616d0000b273350fe52fe51edbfe385b6228',
  },
  {
    title: 'Raataan Lambiyan',
    artist: 'Jubin Nautiyal, Asees Kaur',
    cover: 'https://i.scdn.co/image/ab67616d00001e02a75c2f26913099a420050f01',
  },
  {
    title: 'Ghungroo',
    artist: 'Arijit Singh, Shilpa Rao',
    cover: 'https://i.scdn.co/image/ab67616d0000b273281650a8e8c5d04658d31ac1',
  },
  {
    title: 'Dil Diyan Gallan',
    artist: 'Atif Aslam',
    cover: 'https://i.scdn.co/image/ab67616d0000b273576521b1bf3ec2fd7fdfcbd5',
  },
  {
    title: 'Kabira',
    artist: 'Tochi Raina, Rekha Bhardwaj',
    cover: 'https://i.scdn.co/image/ab67616d0000b273707ea5b8023ac77d31756ed4',
  },
];

const MotionBox = motion(Box);

const Carousel = () => {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % tracks.length);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <Box w="100%" h="100vh" display="flex" alignItems="center" justifyContent="center" bg="gray.900" position="relative">
      <AnimatePresence initial={false}>
        <MotionBox
          key={index}
          initial={{ x: 300, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: -300, opacity: 0 }}
          transition={{ duration: 0.7 }}
          position="absolute"
          w="320px"
          h="420px"
          bg="black"
          borderRadius="2xl"
          boxShadow="2xl"
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          p={8}
        >
          <Image src={tracks[index].cover} alt={tracks[index].title} w="180px" h="180px" borderRadius="lg" mb={6} />
          <Heading size="md" color="spotify.green" mb={2} textAlign="center">{tracks[index].title}</Heading>
          <Text color="spotify.lightGray" fontSize="lg" textAlign="center">{tracks[index].artist}</Text>
        </MotionBox>
      </AnimatePresence>
    </Box>
  );
};

const Login = () => {
  const handleLogin = () => {
    // TODO: Implement Spotify OAuth login
    window.location.href = `${import.meta.env.VITE_API_URL}/auth/spotify`;
  };

  return (
    <Flex w="100vw" h="100vh" bg="black">
      {/* Left: Login Section */}
      <Flex flex="1" direction="column" align="center" justify="center" h="100vh">
        {/* Big Logo */}
        <Flex w="100%" justify="center" mb={10}>
          <Image
            src="/spotify-logo.svg"
            alt="Spotify Logo"
            w="90%"
            maxW="700px"
            h="auto"
            objectFit="contain"
            mb={10}
          />
        </Flex>
        {/* Content */}
        <VStack align="flex-start" spacing={10} maxW="lg" w="100%">
          <Heading size="2xl" bgGradient="linear(to-r, spotify.green, green.400)" bgClip="text" letterSpacing="tight">
            Spotify Analytics
          </Heading>
          <Text fontSize="xl" color="spotify.blue">
            Discover your listening habits and explore your music taste
          </Text>
          <Button
            variant="solid"
            size="lg"
            onClick={handleLogin}
            px={8}
            py={6}
            fontSize="lg"
            rounded="full"
            bg="spotify.green"
            color="white"
            _hover={{ bg: '#1ed760', transform: 'scale(1.05)' }}
            transition="all 0.2s ease-in-out"
          >
            Login with Spotify
          </Button>
        </VStack>
      </Flex>
      {/* Right: Carousel Section */}
      <Box flex="1.2" display={{ base: 'none', md: 'block' }}>
        <Carousel />
      </Box>
    </Flex>
  );
};

export default Login; 