'use client'

import { Box } from '@chakra-ui/react'
import { forwardRef } from 'react'

export const Card = forwardRef(function Card(props, ref) {
  const { children, ...rest } = props
  return (
    <Box
      ref={ref}
      bg="bg.panel"
      borderRadius="md"
      borderWidth="1px"
      borderColor="border"
      shadow="sm"
      _dark={{
        bg: "bg.panel",
        borderColor: "border",
      }}
      {...rest}
    >
      {children}
    </Box>
  )
})

export const CardBody = forwardRef(function CardBody(props, ref) {
  const { children, ...rest } = props
  return (
    <Box ref={ref} p="6" {...rest}>
      {children}
    </Box>
  )
})

export const CardHeader = forwardRef(function CardHeader(props, ref) {
  const { children, ...rest } = props
  return (
    <Box ref={ref} p="6" pb="0" {...rest}>
      {children}
    </Box>
  )
})

export const CardFooter = forwardRef(function CardFooter(props, ref) {
  const { children, ...rest } = props
  return (
    <Box ref={ref} p="6" pt="0" {...rest}>
      {children}
    </Box>
  )
})

Card.Body = CardBody
Card.Header = CardHeader
Card.Footer = CardFooter
Card.Root = Card
