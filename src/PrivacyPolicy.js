import React from 'react';
import { 
  Box, 
  Container, 
  Flex, 
  Heading, 
  Text, 
  Button, 
  HStack,
  VStack,
  Icon,
  Badge,
  SimpleGrid,
  List
} from '@chakra-ui/react';
import { Card } from './components/ui/card';
import Breadcrumb from './components/Breadcrumb';
import { 
  FiLock,
  FiUserCheck,
  FiFileText,
  FiGlobe
} from 'react-icons/fi';

function PrivacyPolicy({ onNavigateHome, onNavigate }) {
  const navigateToPage = onNavigate || onNavigateHome;
  
  return (
    <Box minH="100vh" bg="bg.canvas">
      {/* Header with Navigation */}
      <Box as="header" borderBottomWidth="1px" borderColor="border">
        <Container maxW="7xl" py="4">
          <Flex justify="space-between" align="center">
            <HStack gap="3">
              <Box p="2" bg="blue.500" borderRadius="md">
                <Icon fontSize="xl" color="white">
                  <FiLock />
                </Icon>
              </Box>
              <Box>
                <Heading size="lg" color="blue.600" _dark={{ color: "blue.300" }}>
                  Privacy Policy & License
                </Heading>
                <Text fontSize="sm" color="fg.muted">
                  Non-Commercial License Terms & Privacy Information
                </Text>
              </Box>
            </HStack>
          </Flex>
          
          {/* Breadcrumb Navigation */}
          <Box pt="4" borderTopWidth="1px" borderColor="border.subtle" mt="4">
            <Breadcrumb currentPage="privacy" onNavigate={navigateToPage} />
          </Box>
        </Container>
      </Box>

      {/* Hero Section */}
      <Box bg="green.50" _dark={{ bg: "green.950" }}>
        <Container maxW="6xl" py="16">
          <VStack gap="8" textAlign="center">
            <VStack gap="4">
              <Badge colorPalette="green" variant="subtle" px="4" py="2">
                🔒 Privacy First
              </Badge>
              <Heading size="3xl" lineHeight="tight">
                Your Privacy & Our License
              </Heading>
              <Text fontSize="lg" color="fg.muted" maxW="2xl">
                File Hash Checker is committed to protecting your privacy and operates under a non-commercial license.
              </Text>
            </VStack>
          </VStack>
        </Container>
      </Box>

      {/* Privacy Overview */}
      <Container maxW="6xl" py="16">
        <VStack gap="16">
          <VStack gap="4" textAlign="center">
            <Heading size="2xl">Privacy Overview</Heading>
            <Text fontSize="lg" color="fg.muted" maxW="2xl">
              We believe in complete transparency about how your data is handled.
            </Text>
          </VStack>

          <SimpleGrid columns={{ base: 1, md: 2 }} gap="6">
            <Card bg="green.50" borderColor="green.200" _dark={{ bg: "green.900", borderColor: "green.700" }}>
              <Card.Body p="8">
                <VStack align="start" gap="4">
                  <HStack gap="3">
                    <Box p="2" bg="green.100" borderRadius="md" _dark={{ bg: "green.800" }}>
                      <Icon fontSize="lg" color="green.500">
                        <FiLock />
                      </Icon>
                    </Box>
                    <Heading size="lg" color="green.700" _dark={{ color: "green.300" }}>
                      Zero Data Collection
                    </Heading>
                  </HStack>
                  <Text fontSize="sm" color="green.700" _dark={{ color: "green.400" }}>
                    <strong>We collect absolutely no personal data.</strong> All file processing happens locally on your machine. 
                    No files, hashes, or personal information ever leaves your computer except when you choose to use VirusTotal.
                  </Text>
                </VStack>
              </Card.Body>
            </Card>

            <Card bg="blue.50" borderColor="blue.200" _dark={{ bg: "blue.900", borderColor: "blue.700" }}>
              <Card.Body p="8">
                <VStack align="start" gap="4">
                  <HStack gap="3">
                    <Box p="2" bg="blue.100" borderRadius="md" _dark={{ bg: "blue.800" }}>
                      <Icon fontSize="lg" color="blue.500">
                        <FiUserCheck />
                      </Icon>
                    </Box>
                    <Heading size="lg" color="blue.700" _dark={{ color: "blue.300" }}>
                      No Tracking or Analytics
                    </Heading>
                  </HStack>
                  <Text fontSize="sm" color="blue.700" _dark={{ color: "blue.400" }}>
                    <strong>No telemetry, cookies, or tracking.</strong> We don't monitor your usage, collect statistics, 
                    or track your behavior. The application works completely offline except for optional VirusTotal integration.
                  </Text>
                </VStack>
              </Card.Body>
            </Card>
          </SimpleGrid>
        </VStack>
      </Container>

      {/* Detailed Privacy Information */}
      <Box bg="bg.subtle">
        <Container maxW="6xl" py="20">
          <VStack gap="16">
            <VStack gap="4" textAlign="center">
              <Heading size="2xl">Detailed Privacy Information</Heading>
              <Text fontSize="lg" color="fg.muted" maxW="2xl">
                Complete transparency about data handling and third-party services.
              </Text>
            </VStack>

            <SimpleGrid columns={{ base: 1, lg: 2 }} gap="8">
              {/* Local Data Storage */}
              <Card>
                <Card.Body p="8">
                  <VStack align="start" gap="6">
                    <HStack gap="3">
                      <Box p="2" bg="purple.50" borderRadius="md" _dark={{ bg: "purple.900" }}>
                        <Icon fontSize="lg" color="purple.500">
                          <FiFileText />
                        </Icon>
                      </Box>
                      <Heading size="lg">Local Data Storage</Heading>
                    </HStack>
                    
                    <VStack align="start" gap="4" w="full">
                      <Text fontSize="sm" fontWeight="medium">What is stored locally:</Text>
                      <List.Root fontSize="sm" color="fg.muted" spacing="2">
                        <List.Item>VirusTotal API key (encrypted in Windows Registry)</List.Item>
                        <List.Item>Application preferences and settings</List.Item>
                        <List.Item>Temporary hash calculation results (session only)</List.Item>
                        <List.Item>Export history and file paths (if enabled)</List.Item>
                      </List.Root>
                      
                      <Text fontSize="sm" fontWeight="medium" pt="2">What is NOT stored:</Text>
                      <List.Root fontSize="sm" color="fg.muted" spacing="2">
                        <List.Item>File contents or file data</List.Item>
                        <List.Item>Personal information or user profiles</List.Item>
                        <List.Item>Usage statistics or analytics</List.Item>
                        <List.Item>Network requests or browsing history</List.Item>
                      </List.Root>
                    </VStack>
                  </VStack>
                </Card.Body>
              </Card>

              {/* Third-Party Services */}
              <Card>
                <Card.Body p="8">
                  <VStack align="start" gap="6">
                    <HStack gap="3">
                      <Box p="2" bg="orange.50" borderRadius="md" _dark={{ bg: "orange.900" }}>
                        <Icon fontSize="lg" color="orange.500">
                          <FiGlobe />
                        </Icon>
                      </Box>
                      <Heading size="lg">Third-Party Services</Heading>
                    </HStack>
                    
                    <VStack align="start" gap="4" w="full">
                      <Text fontSize="sm" fontWeight="medium">VirusTotal Integration (Optional):</Text>
                      <List.Root fontSize="sm" color="fg.muted" spacing="2">
                        <List.Item>Only file hashes are sent, never file contents</List.Item>
                        <List.Item>Requires your explicit consent and API key</List.Item>
                        <List.Item>Subject to VirusTotal's privacy policy</List.Item>
                        <List.Item>Can be completely disabled</List.Item>
                      </List.Root>
                      
                      <Text fontSize="sm" fontWeight="medium" pt="2">No other external services:</Text>
                      <List.Root fontSize="sm" color="fg.muted" spacing="2">
                        <List.Item>No cloud storage or backup services</List.Item>
                        <List.Item>No crash reporting or error tracking</List.Item>
                        <List.Item>No update servers or auto-update checks</List.Item>
                        <List.Item>No social media or sharing integrations</List.Item>
                      </List.Root>
                    </VStack>
                  </VStack>
                </Card.Body>
              </Card>
            </SimpleGrid>
          </VStack>
        </Container>
      </Box>

      {/* License Section */}
      <Container maxW="6xl" py="20">
        <VStack gap="16">
          <VStack gap="4" textAlign="center">
            <Badge colorPalette="blue" variant="subtle" fontSize="sm" px="4" py="2">
              📄 Non-Commercial License
            </Badge>
            <Heading size="2xl">License Terms</Heading>
            <Text fontSize="lg" color="fg.muted" maxW="2xl">
              File Hash Checker is free for personal, educational, and non-profit use.
            </Text>
          </VStack>

          {/* License Summary Cards */}
          <SimpleGrid columns={{ base: 1, md: 3 }} gap="6">
            <Card bg="green.50" borderColor="green.200" _dark={{ bg: "green.900", borderColor: "green.700" }}>
              <Card.Body p="6" textAlign="center">
                <VStack gap="4">
                  <Text fontSize="3xl">✅</Text>
                  <Heading size="md" color="green.700" _dark={{ color: "green.300" }}>
                    Permitted Uses
                  </Heading>
                  <List.Root fontSize="sm" color="green.700" _dark={{ color: "green.400" }} textAlign="left" spacing="1">
                    <List.Item>Personal use and education</List.Item>
                    <List.Item>Academic research</List.Item>
                    <List.Item>Non-profit organizations</List.Item>
                    <List.Item>Government/public sector</List.Item>
                    <List.Item>Open source contributions</List.Item>
                  </List.Root>
                </VStack>
              </Card.Body>
            </Card>

            <Card bg="red.50" borderColor="red.200" _dark={{ bg: "red.900", borderColor: "red.700" }}>
              <Card.Body p="6" textAlign="center">
                <VStack gap="4">
                  <Text fontSize="3xl">❌</Text>
                  <Heading size="md" color="red.700" _dark={{ color: "red.300" }}>
                    Prohibited Uses
                  </Heading>
                  <List.Root fontSize="sm" color="red.700" _dark={{ color: "red.400" }} textAlign="left" spacing="1">
                    <List.Item>Commercial use of any kind</List.Item>
                    <List.Item>Business operations</List.Item>
                    <List.Item>Selling or monetizing</List.Item>
                    <List.Item>Profit-generating activities</List.Item>
                    <List.Item>Commercial consulting</List.Item>
                  </List.Root>
                </VStack>
              </Card.Body>
            </Card>

            <Card bg="blue.50" borderColor="blue.200" _dark={{ bg: "blue.900", borderColor: "blue.700" }}>
              <Card.Body p="6" textAlign="center">
                <VStack gap="4">
                  <Text fontSize="3xl">📝</Text>
                  <Heading size="md" color="blue.700" _dark={{ color: "blue.300" }}>
                    Conditions
                  </Heading>
                  <List.Root fontSize="sm" color="blue.700" _dark={{ color: "blue.400" }} textAlign="left" spacing="1">
                    <List.Item>License notice required</List.Item>
                    <List.Item>Attribution preserved</List.Item>
                    <List.Item>No warranty provided</List.Item>
                    <List.Item>Derivatives non-commercial</List.Item>
                    <List.Item>Author contact for commercial</List.Item>
                  </List.Root>
                </VStack>
              </Card.Body>
            </Card>
          </SimpleGrid>

          {/* Full License Text */}
          <Card>
            <Card.Body p="8">
              <VStack align="start" gap="6">
                <Heading size="lg">Full License Text</Heading>
                <Box 
                  bg="gray.50" 
                  p="6" 
                  borderRadius="md" 
                  borderWidth="1px" 
                  borderColor="gray.200"
                  _dark={{ bg: "gray.900", borderColor: "gray.700" }}
                  maxH="400px"
                  overflowY="auto"
                  w="full"
                >
                  <Text fontSize="sm" fontFamily="mono" whiteSpace="pre-line" color="gray.700" _dark={{ color: "gray.300" }}>
{`NON-COMMERCIAL LICENSE

Copyright (c) 2025 File Hash Calculator Project

TERMS AND CONDITIONS:

1. PERMITTED USES:
   - Personal use and education
   - Academic research and study
   - Open source contributions
   - Non-profit organization use
   - Government and public sector use (non-commercial)

2. PROHIBITED USES:
   - Commercial use of any kind
   - Business operations or commercial services
   - Selling, licensing, or monetizing the software
   - Using for profit-generating activities
   - Incorporating into commercial products
   - Using algorithms or code for commercial gain
   - Consulting or professional services using this software

3. PERMISSIONS:
   - Use, copy, modify, and distribute for non-commercial purposes
   - Create derivative works for personal/educational use
   - Contribute improvements back to the project

4. CONDITIONS:
   - This license notice must be included in all copies
   - Any derivative work must maintain this non-commercial license
   - Attribution to original author(s) must be preserved
   - No warranty or liability is provided

5. COMMERCIAL LICENSING:
   - Contact the author for commercial licensing inquiries
   - Commercial use requires explicit written permission
   - Violation of these terms may result in legal action

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

For commercial licensing inquiries, please contact the project maintainer.`}
                  </Text>
                </Box>
              </VStack>
            </Card.Body>
          </Card>
        </VStack>
      </Container>

      {/* Contact Section */}
      <Box bg="blue.50" _dark={{ bg: "blue.950" }}>
        <Container maxW="4xl" py="16">
          <VStack gap="8" textAlign="center">
            <VStack gap="4">
              <Badge colorPalette="blue" variant="subtle" fontSize="sm" px="4" py="2">
                📞 Questions?
              </Badge>
              <Heading size="2xl">Need Clarification?</Heading>
              <Text fontSize="lg" color="fg.muted" maxW="xl">
                If you have questions about privacy, licensing, or commercial use, we're here to help.
              </Text>
            </VStack>

            <HStack gap="4" flexDirection={{ base: "column", sm: "row" }}>
              <Button 
                size="lg" 
                colorPalette="blue" 
                variant="solid"
                as="a"
                href="https://github.com/subham-04/file-hash-checker/issues"
                target="_blank"
                rel="noopener noreferrer"
              >
                <FiFileText />
                Report Issues
              </Button>
              <Button 
                size="lg" 
                variant="outline"
                as="a"
                href="https://github.com/subham-04/file-hash-checker"
                target="_blank"
                rel="noopener noreferrer"
              >
                <FiGlobe />
                View on GitHub
              </Button>
            </HStack>

            <Text fontSize="sm" color="fg.muted">
              For commercial licensing inquiries, please create a GitHub issue or contact the project maintainer.
            </Text>
          </VStack>
        </Container>
      </Box>

      {/* Footer */}
      <Box bg="bg.subtle" borderTopWidth="1px">
        <Container maxW="6xl" py="12">
          <VStack gap="8">
            <HStack justify="center" w="full">
              <HStack gap="4" fontSize="sm" color="fg.muted">
                <Text>© 2025 Non-Commercial License</Text>
                <Text>•</Text>
                <Text>Privacy First</Text>
                <Text>•</Text>
                <Text>Zero Telemetry</Text>
              </HStack>
            </HStack>
            
            <Text fontSize="sm" color="fg.muted" textAlign="center">
              Built with ❤️ for the cybersecurity community
            </Text>
          </VStack>
        </Container>
      </Box>
    </Box>
  );
}

export default PrivacyPolicy;
